"""Umumiy xavfsizlik yordamchilari: parol xeshi (scrypt), tasodifiy tokenlar, oddiy rate limit."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import threading
import time
from collections import defaultdict, deque

_N, _R, _P = 2 ** 14, 8, 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)
    return f"scrypt${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, dk_hex = stored.split("$")
        if algo != "scrypt":
            return False
        dk = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=_N, r=_R, p=_P, dklen=32)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, TypeError):
        return False


def new_token(nbytes: int = 24) -> str:
    return secrets.token_urlsafe(nbytes)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class RateLimiter:
    """Xotiradagi sirpanuvchi oyna: `hit(key)` limitdan oshsa False qaytaradi."""

    def __init__(self, limit: int, window_s: float):
        self.limit, self.window = limit, window_s
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def client_ip(request) -> str:
    """uvicorn --proxy-headers bilan request.client.host = haqiqiy IP (nginx X-Forwarded-For)."""
    try:
        return request.client.host or "?"
    except AttributeError:
        return "?"
