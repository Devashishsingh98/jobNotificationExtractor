"""Tests for authentication helpers."""

import pytest
import jwt
from datetime import datetime, timezone
from app.routes.auth import create_token, verify_token


class TestCreateToken:
    def test_creates_valid_jwt(self):
        token = create_token("test-user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_sub(self):
        token = create_token("user-abc")
        from app.config import get_settings
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "user-abc"

    def test_token_has_expiry(self):
        token = create_token("user-abc")
        from app.config import get_settings
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert "exp" in payload
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()


class TestVerifyToken:
    def test_verify_valid_token(self):
        token = create_token("user-xyz")
        user_id = verify_token(token)
        assert user_id == "user-xyz"

    def test_verify_invalid_token(self):
        with pytest.raises(Exception):
            verify_token("invalid.token.here")

    def test_verify_tampered_token(self):
        token = create_token("user-abc")
        # Tamper with the token
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(Exception):
            verify_token(tampered)
