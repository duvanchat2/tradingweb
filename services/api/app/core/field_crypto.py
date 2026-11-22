"""Encryption for sensitive application fields stored in PostgreSQL."""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


def _cipher() -> Fernet:
    key = hashlib.sha256(get_settings().jwt_secret.encode('utf-8')).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_field(value: str) -> str:
    return _cipher().encrypt(value.encode('utf-8')).decode('ascii')


def decrypt_field(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return _cipher().decrypt(value.encode('ascii')).decode('utf-8')
    except InvalidToken:
        return None
