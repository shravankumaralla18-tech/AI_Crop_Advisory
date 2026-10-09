import pytest
from pydantic import ValidationError

from app.schemas.user_schema import UserCreate, UserLogin
from app.utils.helpers import parse_class_name
from app.utils.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("correct horse battery")
    assert hashed != "correct horse battery"
    assert verify_password("correct horse battery", hashed)
    assert not verify_password("wrong password", hashed)


def test_passwords_over_bcrypt_byte_limit_are_rejected():
    with pytest.raises(ValidationError):
        UserCreate(name="Farmer", email="farmer@example.com", password="a" * 73)
    with pytest.raises(ValidationError):
        UserLogin(email="farmer@example.com", password="a" * 73)
    with pytest.raises(ValueError):
        hash_password("a" * 73)


def test_token_roundtrip():
    token = create_access_token("abc123")
    assert decode_access_token(token) == "abc123"
    assert decode_access_token(token + "x") is None


def test_parse_class_name():
    assert parse_class_name("Tomato___Early_blight") == ("Tomato", "Early blight", False)
    assert parse_class_name("Corn_(maize)___Common_rust_") == ("Corn (maize)", "Common rust", False)
    assert parse_class_name("Apple___healthy")[2] is True
