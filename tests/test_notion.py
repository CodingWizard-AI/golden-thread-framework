"""Tests for Notion integration."""

import json
import time
from pathlib import Path

import pytest
import responses

from golden_thread import NotionError
from golden_thread.config import NotionConfig
from golden_thread.notion.client import NotionClient
from golden_thread.notion.registry import NotionRegistry


class TestNotionClient:
    """Test Notion API client."""

    def test_client_initialization(self, tmp_path):
        """Test client initialization."""
        config = NotionConfig(
            api_token="test_token",
            cache_enabled=True,
            cache_directory=str(tmp_path / ".cache"),
        )

        client = NotionClient(config)

        assert client.api_token == "test_token"
        assert client.cache_enabled is True
        assert client.cache_dir.exists()

    @responses.activate
    def test_search_database_success(self, tmp_path):
        """Test successful database query."""
        responses.add(
            responses.POST,
            "https://api.notion.com/v1/databases/test-db-123/query",
            json={"results": [{"id": "page-1", "properties": {}}], "has_more": False},
            status=200,
        )

        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)

        results = client.search_database("test-db-123")

        assert len(results) == 1
        assert results[0]["id"] == "page-1"

    @responses.activate
    def test_search_database_with_filter(self, tmp_path):
        """Test database query with filter."""
        def request_callback(request):
            payload = json.loads(request.body)
            assert "filter" in payload
            assert payload["filter"]["property"] == "ID"
            return (200, {}, json.dumps({"results": [], "has_more": False}))

        responses.add_callback(
            responses.POST,
            "https://api.notion.com/v1/databases/test-db-123/query",
            callback=request_callback,
        )

        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)

        filter_params = {"property": "ID", "title": {"equals": "FEAT-001"}}
        results = client.search_database("test-db-123", filter_params)

        assert isinstance(results, list)

    @responses.activate
    def test_search_database_pagination(self, tmp_path):
        """Test pagination handling."""
        # First response with has_more=True
        responses.add(
            responses.POST,
            "https://api.notion.com/v1/databases/test-db-123/query",
            json={
                "results": [{"id": "page-1"}],
                "has_more": True,
                "next_cursor": "cursor-123",
            },
            status=200,
        )

        # Second response with has_more=False
        responses.add(
            responses.POST,
            "https://api.notion.com/v1/databases/test-db-123/query",
            json={"results": [{"id": "page-2"}], "has_more": False},
            status=200,
        )

        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)

        results = client.search_database("test-db-123")

        # Should combine both pages
        assert len(results) == 2
        assert results[0]["id"] == "page-1"
        assert results[1]["id"] == "page-2"

    @responses.activate
    def test_search_database_404_error(self, tmp_path):
        """Test handling of 404 error."""
        responses.add(
            responses.POST,
            "https://api.notion.com/v1/databases/test-db-123/query",
            json={"object": "error", "status": 404},
            status=404,
        )

        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)

        with pytest.raises(NotionError, match="not found"):
            client.search_database("test-db-123")

    @responses.activate
    def test_search_database_401_error(self, tmp_path):
        """Test handling of authentication error."""
        responses.add(
            responses.POST,
            "https://api.notion.com/v1/databases/test-db-123/query",
            json={"object": "error", "status": 401},
            status=401,
        )

        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)

        with pytest.raises(NotionError, match="authentication"):
            client.search_database("test-db-123")

    def test_caching(self, tmp_path):
        """Test that caching works."""
        config = NotionConfig(
            api_token="test_token",
            cache_enabled=True,
            cache_directory=str(tmp_path / ".cache"),
            cache_ttl=3600,
        )
        client = NotionClient(config)

        # Manually set cached data
        cache_key = client._get_cache_key("test_key")
        test_data = {"test": "data"}
        client._set_cached(cache_key, test_data)

        # Retrieve from cache
        cached_data = client._get_cached(cache_key)
        assert cached_data == test_data

    def test_cache_expiry(self, tmp_path):
        """Test that cache expires after TTL."""
        config = NotionConfig(
            api_token="test_token",
            cache_enabled=True,
            cache_directory=str(tmp_path / ".cache"),
            cache_ttl=1,  # 1 second TTL
        )
        client = NotionClient(config)

        # Set cached data
        cache_key = client._get_cache_key("test_key")
        test_data = {"test": "data"}
        client._set_cached(cache_key, test_data)

        # Wait for cache to expire
        time.sleep(2)

        # Should return None (expired)
        cached_data = client._get_cached(cache_key)
        assert cached_data is None

    @responses.activate
    def test_get_page_success(self, tmp_path):
        """Test successful page retrieval."""
        responses.add(
            responses.GET,
            "https://api.notion.com/v1/pages/page-123",
            json={"id": "page-123", "properties": {}},
            status=200,
        )

        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)

        page = client.get_page("page-123")

        assert page["id"] == "page-123"

    def test_clear_cache(self, tmp_path):
        """Test clearing cache."""
        config = NotionConfig(
            api_token="test_token",
            cache_enabled=True,
            cache_directory=str(tmp_path / ".cache"),
        )
        client = NotionClient(config)

        # Create some cache files
        cache_key = client._get_cache_key("test_key")
        client._set_cached(cache_key, {"test": "data"})

        assert client._get_cached(cache_key) is not None

        # Clear cache
        client.clear_cache()

        # Cache should be empty
        assert client._get_cached(cache_key) is None


class TestNotionRegistry:
    """Test Notion registry interface."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)
        database_ids = {"BR": "db-br-123", "UR": "db-ur-123"}

        registry = NotionRegistry(client, database_ids)

        assert registry.client == client
        assert registry.database_ids == database_ids

    def test_validate_id_format(self):
        """Test ID format validation."""
        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)
        registry = NotionRegistry(client, {})

        # Valid IDs
        assert registry.validate_id_format("BR-AUTH-001") is True
        assert registry.validate_id_format("FEAT-CV-123") is True
        assert registry.validate_id_format("FR-TEST-999") is True
        assert registry.validate_id_format("REST-HEALTH-001") is True

        # Invalid IDs
        assert registry.validate_id_format("INVALID") is False
        assert registry.validate_id_format("BR-001") is False
        assert registry.validate_id_format("BR-auth-001") is False  # Lowercase

    def test_extract_id_type(self):
        """Test extracting ID type from ID string."""
        config = NotionConfig(api_token="test_token", cache_enabled=False)
        client = NotionClient(config)
        registry = NotionRegistry(client, {})

        assert registry._extract_id_type("BR-AUTH-001") == "BR"
        assert registry._extract_id_type("FEAT-CV-123") == "FEAT"
        assert registry._extract_id_type("REST-HEALTH-001") == "REST"
        assert registry._extract_id_type("INVALID") is None
