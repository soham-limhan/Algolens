from app.auth.security import hash_password, verify_password


def test_long_passwords_are_supported_by_bcrypt() -> None:
    long_password = "p" * 90

    hashed = hash_password(long_password)

    assert verify_password(long_password, hashed) is True
