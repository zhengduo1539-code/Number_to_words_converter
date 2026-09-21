from types import SimpleNamespace

from app.config import Settings
from app.utils.security import is_admin


def test_admin_ids_are_numeric_and_exact():
    settings = Settings(ADMIN_IDS="123, 456")
    assert is_admin(SimpleNamespace(id=123), settings)
    assert not is_admin(SimpleNamespace(id=999, username="123"), settings)
