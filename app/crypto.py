import os
import base64
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

_ITERATIONS = 100000
_SALT_LEN = 16
_NONCE_LEN = 12
_KEY_LEN = 32


def derive_key(master_password: str, salt: bytes | None = None, iterations: int | None = None) -> tuple[bytes, bytes]:
    """PBKDF2-HMAC-SHA256 派生 AES-256 密钥，返回 (key, salt)。"""
    if salt is None:
        salt = os.urandom(_SALT_LEN)
    if iterations is None:
        iterations = _ITERATIONS
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_LEN,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    key = kdf.derive(master_password.encode('utf-8'))
    return key, salt


def encrypt(plaintext: str, key: bytes) -> tuple[str, str]:
    """AES-256-GCM 加密，返回 (base64_ciphertext, base64_nonce)。"""
    nonce = os.urandom(_NONCE_LEN)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(ct).decode(), base64.b64encode(nonce).decode()


def decrypt(ciphertext_b64: str, nonce_b64: str, key: bytes) -> str:
    """AES-256-GCM 解密，返回明文字符串。"""
    aesgcm = AESGCM(key)
    ct = base64.b64decode(ciphertext_b64)
    nonce = base64.b64decode(nonce_b64)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode('utf-8')


def hash_password(password: str) -> str:
    """对密码进行 SHA-256 哈希（用于验证主密码，非加密存储）。"""
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
