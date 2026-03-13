from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, stored_password: str | None) -> bool:
    if not stored_password:
        return False

    scheme = pwd_context.identify(stored_password)
    if scheme:
        return pwd_context.verify(plain_password, stored_password)

    return plain_password == stored_password
