from jose import jwt

from app.core.config import get_settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("mysecretpassword")
    assert hashed != "mysecretpassword"
    assert verify_password("mysecretpassword", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_contains_subject():
    token = create_access_token({"sub": "user@example.com"})
    secret = get_settings().SECRET_KEY
    payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    assert payload["sub"] == "user@example.com"
    assert "exp" in payload


def test_different_passwords_produce_different_hashes():
    h1 = hash_password("password-one")
    h2 = hash_password("password-two")
    assert h1 != h2
