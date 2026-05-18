"""Cache module"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CacheEntry(BaseModel):
    """Cache entry."""

    data: List[Dict[str, Any]]
    expires_at: datetime


class ReportCache:
    """Report cache."""

    _cache_store: Dict[str, CacheEntry] = {}
    TTL_HOURS = 1

    @classmethod
    def generate_key(cls, report_type: str, filters: BaseModel) -> str:
        """Generate md5 hash from report_type + ordered filters."""
        filters_str = json.dumps(
            filters.model_dump(exclude_none=True), sort_keys=True, ensure_ascii=False
        )
        raw_key = f"{report_type}:{filters_str}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def set(
        cls, report_type: str, filters: BaseModel, data: List[Dict[str, Any]]
    ) -> str:
        """Stores data and returns the cache_key."""
        cls._cleanup_expired()
        cache_key = cls.generate_key(report_type, filters)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=cls.TTL_HOURS)
        cls._cache_store[cache_key] = CacheEntry(data=data, expires_at=expires_at)
        return cache_key

    @classmethod
    def get(
        cls, report_type: str, filters: BaseModel
    ) -> Optional[List[Dict[str, Any]]]:
        """Returns data or None if expired/missing."""
        cls._cleanup_expired()
        cache_key = cls.generate_key(report_type, filters)

        entry = cls._cache_store.get(cache_key)
        if entry:
            return entry.data
        return None

    @classmethod
    def _cleanup_expired(cls) -> None:
        """Removes expired TTL entries."""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key for key, entry in cls._cache_store.items() if entry.expires_at <= now
        ]
        for key in expired_keys:
            del cls._cache_store[key]

    @classmethod
    def clear_all(cls) -> None:
        """Clears all cache"""
        cls._cache_store.clear()
