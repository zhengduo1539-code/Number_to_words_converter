from types import SimpleNamespace

from app.config import Settings
from app.utils.security import is_admin


def test_admin_ids_are_numeric_and_exact():
    settings = Settings(ADMIN_IDS="123, 456")
    assert is_admin(SimpleNamespace(id=123), settings)
    assert not is_admin(SimpleNamespace(id=999, username="123"), settings)


def test_admin_ids_are_parsed_from_environment(monkeypatch):
    monkeypatch.setenv("ADMIN_IDS", "123, 456")
    settings = Settings(_env_file=None)
    assert settings.admin_ids == [123, 456]


def test_admin_ids_accept_json_array():
    settings = Settings(ADMIN_IDS="[123, 456]")
    assert settings.admin_ids == [123, 456]
