"""Notion API REST client with caching and rate limiting."""

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ..config import NotionConfig
from .. import NotionError


class NotionClient:
    """REST API client for Notion with caching and rate limiting."""

    def __init__(self, config: NotionConfig):
        """
        Initialize Notion client.

        Args:
            config: Notion configuration
        """
        self.api_token = config.api_token
        self.version = config.version
        self.timeout = config.timeout
        self.base_url = "https://api.notion.com/v1"

        # Rate limiting (Notion limit: 3 requests/second)
        self.rate_limit = 3  # requests per second
        self.last_request_time = 0.0

        # Caching
        self.cache_enabled = config.cache_enabled
        self.cache_ttl = config.cache_ttl
        self.cache_dir = Path(config.cache_directory)
        if self.cache_enabled:
            self.cache_dir.mkdir(exist_ok=True, parents=True)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for Notion API."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Notion-Version": self.version,
            "Content-Type": "application/json",
        }

    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        min_interval = 1.0 / self.rate_limit

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self.last_request_time = time.time()

    def _get_cache_key(self, key_data: str) -> str:
        """Generate cache key from data."""
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path to cache file."""
        return self.cache_dir / f"{cache_key}.json"

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """
        Retrieve from cache if valid.

        Args:
            cache_key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        if not self.cache_enabled:
            return None

        cache_path = self._get_cache_path(cache_key)
        if not cache_path.exists():
            return None

        # Check TTL
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > timedelta(seconds=self.cache_ttl):
            # Cache expired, delete it
            cache_path.unlink()
            return None

        try:
            with open(cache_path) as f:
                return json.load(f)
        except Exception:
            # Cache corrupted, delete it
            cache_path.unlink()
            return None

    def _set_cached(self, cache_key: str, data: Any):
        """
        Save to cache.

        Args:
            cache_key: Cache key
            data: Data to cache
        """
        if not self.cache_enabled:
            return

        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f)
        except Exception:
            # Ignore cache write failures
            pass

    def search_database(
        self, database_id: str, filter_params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query a Notion database.

        Args:
            database_id: Notion database ID
            filter_params: Optional filter parameters

        Returns:
            List of page results

        Raises:
            NotionError: If API request fails
        """
        # Generate cache key
        cache_key = self._get_cache_key(f"db_{database_id}_{str(filter_params)}")

        # Check cache
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Make request
        self._rate_limit()

        url = f"{self.base_url}/databases/{database_id}/query"
        payload = {"page_size": 100}
        if filter_params:
            payload["filter"] = filter_params

        results = []
        has_more = True
        next_cursor = None

        try:
            while has_more:
                if next_cursor:
                    payload["start_cursor"] = next_cursor

                response = requests.post(
                    url, headers=self._get_headers(), json=payload, timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()
                results.extend(data.get("results", []))

                has_more = data.get("has_more", False)
                next_cursor = data.get("next_cursor")

                # Rate limit subsequent requests
                if has_more:
                    self._rate_limit()

        except requests.Timeout:
            raise NotionError(f"Request timeout querying database {database_id}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise NotionError(
                    f"Database not found: {database_id}\n"
                    f"Please check your database IDs in the configuration."
                )
            elif e.response.status_code == 401:
                raise NotionError(
                    "Notion API authentication failed. Please check your API token."
                )
            elif e.response.status_code == 429:
                raise NotionError("Notion API rate limit exceeded. Please try again later.")
            else:
                raise NotionError(f"Notion API error: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            raise NotionError(f"Failed to query database {database_id}: {e}")

        # Cache results
        self._set_cached(cache_key, results)
        return results

    def get_page(self, page_id: str) -> Dict:
        """
        Retrieve a single page.

        Args:
            page_id: Notion page ID

        Returns:
            Page data

        Raises:
            NotionError: If API request fails
        """
        # Generate cache key
        cache_key = self._get_cache_key(f"page_{page_id}")

        # Check cache
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Make request
        self._rate_limit()

        url = f"{self.base_url}/pages/{page_id}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            # Cache result
            self._set_cached(cache_key, result)
            return result

        except requests.Timeout:
            raise NotionError(f"Request timeout retrieving page {page_id}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise NotionError(f"Page not found: {page_id}")
            elif e.response.status_code == 401:
                raise NotionError(
                    "Notion API authentication failed. Please check your API token."
                )
            else:
                raise NotionError(f"Notion API error: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            raise NotionError(f"Failed to retrieve page {page_id}: {e}")

    def clear_cache(self):
        """Clear all cached data."""
        if self.cache_enabled and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
