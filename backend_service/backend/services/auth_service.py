import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.services.db import AuthToken, AuthUser, get_session


def _utcnow() -> str:
    return datetime.now(UTC)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000,
    ).hex()


def register_user(name: str, username: str, email: str, password: str) -> dict:
    user_id = str(uuid.uuid4())
    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    created_at = _utcnow()

    try:
        with get_session() as session:
            session.add(
                AuthUser(
                    user_id=user_id,
                    name=name,
                    username=username.lower(),
                    email=email.lower(),
                    password_hash=password_hash,
                    password_salt=salt,
                    created_at=created_at,
                )
            )
            session.commit()
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Email or username is already registered") from exc

    return create_token_for_user(user_id)


def authenticate_user(email: str, password: str) -> dict:
    with get_session() as session:
        row = session.scalar(select(AuthUser).where(AuthUser.email == email.lower()))

    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    expected = _hash_password(password, row.password_salt)
    if not hmac.compare_digest(expected, row.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return create_token_for_user(row.user_id)


def create_token_for_user(user_id: str) -> dict:
    token = secrets.token_urlsafe(32)
    created_at = _utcnow()
    with get_session() as session:
        session.add(AuthToken(token=token, user_id=user_id, created_at=created_at))
        row = session.get(AuthUser, user_id)
        session.commit()

    return {
        "token": token,
        "user_id": row.user_id,
        "email": row.email,
        "name": row.name,
        "username": row.username or row.email.split("@")[0],
    }


def get_user_by_token(token: str) -> dict:
    with get_session() as session:
        row = session.execute(
            select(AuthUser)
            .join(AuthToken, AuthToken.user_id == AuthUser.user_id)
            .where(AuthToken.token == token)
        ).scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return {
        "user_id": row.user_id,
        "email": row.email,
        "name": row.name,
        "username": row.username or row.email.split("@")[0],
        "auth_provider": "local",
    }


def upsert_external_user(user: dict) -> dict:
    username = (user.get("username") or user.get("email", "user").split("@")[0]).lower()
    with get_session() as session:
        existing = session.get(AuthUser, user["user_id"])
        if existing:
            existing.name = user["name"]
            existing.username = username
            existing.email = user["email"].lower()
        else:
            session.add(
                AuthUser(
                    user_id=user["user_id"],
                    name=user["name"],
                    username=username,
                    email=user["email"].lower(),
                    password_hash="external-auth",
                    password_salt="external-auth",
                    created_at=_utcnow(),
                )
            )
        session.commit()
    return {
        "user_id": user["user_id"],
        "email": user["email"].lower(),
        "name": user["name"],
        "username": username,
        "auth_provider": user.get("auth_provider", "external"),
    }
