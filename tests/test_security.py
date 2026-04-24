"""Tests for API key security helpers."""

import pytest

from app.config import settings
from app.errors import AuthenticationError
from app.security import require_api_key


def test_require_api_key_accepts_matching_key() -> None:
    assert require_api_key(settings.api_key) is None


def test_require_api_key_rejects_invalid_key() -> None:
    with pytest.raises(AuthenticationError) as error:
        require_api_key("wrong-key")

    assert error.value.status_code == 401
    assert error.value.error == "unauthorized"
    assert error.value.message == "Invalid API key."
