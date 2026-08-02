"""API key authentication provider."""

from __future__ import annotations

import secrets
import threading

from traceforge.security.exceptions import InvalidTokenError
from traceforge.security.models.permissions import Permission, Role
from traceforge.security.models.user import User


class ApiKeyEntry:
    """Internal mutable entry for an API key in the registry."""

    def __init__(self, key: str, user: User, enabled: bool = True) -> None:
        self.key = key
        self.user = user
        self.enabled = enabled


class ApiKeyProvider:
    """In-memory API key registry for validation, rotation, and disabling."""

    def __init__(self) -> None:
        self._keys: dict[str, ApiKeyEntry] = {}
        self._lock = threading.RLock()

    def register_key(self, user: User, key: str | None = None) -> str:
        """Register a new API key for a user. Returns the key string."""
        with self._lock:
            api_key = key or secrets.token_urlsafe(32)
            self._keys[api_key] = ApiKeyEntry(key=api_key, user=user)
            return api_key

    def validate_key(self, key: str) -> User:
        """Validate an API key and return the associated User."""
        with self._lock:
            entry = self._keys.get(key)
            if entry is None:
                raise InvalidTokenError("Invalid API key")
            if not entry.enabled:
                raise InvalidTokenError("API key is disabled")
            return entry.user

    def rotate_key(self, old_key: str) -> str:
        """Rotate an API key: disable old, issue new key for the same user."""
        with self._lock:
            entry = self._keys.get(old_key)
            if entry is None:
                raise InvalidTokenError("Cannot rotate: API key not found")
            entry.enabled = False
            new_key = secrets.token_urlsafe(32)
            self._keys[new_key] = ApiKeyEntry(key=new_key, user=entry.user)
            return new_key

    def disable_key(self, key: str) -> None:
        """Disable an API key."""
        with self._lock:
            entry = self._keys.get(key)
            if entry is None:
                raise InvalidTokenError("Cannot disable: API key not found")
            entry.enabled = False
