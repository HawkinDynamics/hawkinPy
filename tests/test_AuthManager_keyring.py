"""Unit tests for the ``keyring`` authMethod added to AuthManager.

These are pure unit tests — they mock the ``keyring`` package and do not touch
the network or require credentials. They validate that the refresh token is
stored to / read from the OS keychain via ``varsManager(method="keyring")`` and
that ``ConfigManager`` accepts the new method.
"""
import sys
from unittest.mock import MagicMock

import pytest

from hdforce.utils import varsManager, ConfigManager


def test_varsManager_keyring_store(monkeypatch):
    """Providing a value stores it in the keychain and returns it."""
    fake_keyring = MagicMock()
    monkeypatch.setitem(sys.modules, "keyring", fake_keyring)

    token = varsManager(name="HD_REFRESH_TOKEN", method="keyring", value="tok123")

    assert token == "tok123"
    fake_keyring.set_password.assert_called_once_with(
        "hdforce", "HD_REFRESH_TOKEN", "tok123"
    )


def test_varsManager_keyring_retrieve(monkeypatch):
    """No value reads the stored token from the keychain."""
    fake_keyring = MagicMock()
    fake_keyring.get_password.return_value = "stored_tok"
    monkeypatch.setitem(sys.modules, "keyring", fake_keyring)

    token = varsManager(name="HD_REFRESH_TOKEN", method="keyring")

    assert token == "stored_tok"
    fake_keyring.get_password.assert_called_once_with("hdforce", "HD_REFRESH_TOKEN")


def test_varsManager_keyring_missing_package(monkeypatch):
    """A helpful ImportError is raised when keyring is not installed."""
    # Setting the module to None makes `import keyring` raise ImportError.
    monkeypatch.setitem(sys.modules, "keyring", None)

    with pytest.raises(ImportError):
        varsManager(name="HD_REFRESH_TOKEN", method="keyring", value="x")


def test_configmanager_accepts_keyring():
    """ConfigManager.set_env_source no longer rejects the keyring method."""
    ConfigManager.set_env_source(
        region="Americas",
        method="keyring",
        fileName=None,
        token_name="HD_REFRESH_TOKEN",
        token="tok123",
    )
    assert ConfigManager.env_method == "keyring"


def test_configmanager_rejects_unknown_method():
    """Unknown methods still raise, keeping the validation intact."""
    with pytest.raises(ValueError):
        ConfigManager.set_env_source(
            region="Americas",
            method="bogus",
            fileName=None,
            token_name="HD_REFRESH_TOKEN",
            token="tok123",
        )
