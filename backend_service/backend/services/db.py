from pathlib import Path 

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "aurora.db"
_ENGINE = None
_SESSION_FACTORY = None


class Base(DeclarativeBase):
    pass


class AuthUser(Base):
    __tablename__ = "auth_users"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    password_salt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    profile: Mapped["UserProfile | None"] = relationship(back_populates="user", cascade="all, delete-orphan")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    token: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[AuthUser] = relationship(back_populates="tokens")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), primary_key=True)
    profile_json: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[AuthUser] = relationship(back_populates="profile")


class PeriodLog(Base):
    __tablename__ = "period_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False, index=True)
    log_json: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class StreakCheckin(Base):
    __tablename__ = "streak_checkins"
    __table_args__ = (UniqueConstraint("user_id", "checkin_date", name="uq_streak_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False, index=True)
    checkin_date: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entry_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False, index=True)
    log_date: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entry_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False, index=True)
    log_date: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entry_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class DietLog(Base):
    __tablename__ = "diet_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False, index=True)
    log_date: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entry_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class SemanticMemory(Base):
    __tablename__ = "semantic_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("auth_users.user_id"), nullable=False, index=True)
    memory_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


def get_database_url() -> str:
    return f"sqlite:///{DB_PATH.as_posix()}"


def get_engine():
    global _ENGINE
    if _ENGINE is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _ENGINE = create_engine(get_database_url(), future=True)
    return _ENGINE


def get_session_factory():
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _SESSION_FACTORY


def get_session():
    return get_session_factory()()


def reset_database_state() -> None:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        _ENGINE.dispose()
    _ENGINE = None
    _SESSION_FACTORY = None


def initialize_database() -> None:
    Base.metadata.create_all(get_engine())
