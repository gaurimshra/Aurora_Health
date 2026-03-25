"""initial schema

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-03-20 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_users",
        sa.Column("user_id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("username", sa.Text(), nullable=True, unique=True),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("password_salt", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "auth_tokens",
        sa.Column("token", sa.Text(), primary_key=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), primary_key=True),
        sa.Column("profile_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "period_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("log_json", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_period_logs_user_id", "period_logs", ["user_id"])
    op.create_index("ix_period_logs_start_date", "period_logs", ["start_date"])
    op.create_table(
        "streak_checkins",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("checkin_date", sa.Text(), nullable=False),
        sa.Column("entry_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "checkin_date", name="uq_streak_user_date"),
    )
    op.create_index("ix_streak_checkins_user_id", "streak_checkins", ["user_id"])
    op.create_index("ix_streak_checkins_checkin_date", "streak_checkins", ["checkin_date"])
    op.create_table(
        "progress_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("log_date", sa.Text(), nullable=False),
        sa.Column("entry_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_progress_logs_user_id", "progress_logs", ["user_id"])
    op.create_index("ix_progress_logs_log_date", "progress_logs", ["log_date"])
    op.create_table(
        "workout_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("log_date", sa.Text(), nullable=False),
        sa.Column("entry_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workout_logs_user_id", "workout_logs", ["user_id"])
    op.create_index("ix_workout_logs_log_date", "workout_logs", ["log_date"])
    op.create_table(
        "diet_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("log_date", sa.Text(), nullable=False),
        sa.Column("entry_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_diet_logs_user_id", "diet_logs", ["user_id"])
    op.create_index("ix_diet_logs_log_date", "diet_logs", ["log_date"])
    op.create_table(
        "semantic_memories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("auth_users.user_id"), nullable=False),
        sa.Column("memory_type", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("embedding_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_semantic_memories_user_id", "semantic_memories", ["user_id"])
    op.create_index("ix_semantic_memories_memory_type", "semantic_memories", ["memory_type"])


def downgrade() -> None:
    op.drop_index("ix_semantic_memories_memory_type", table_name="semantic_memories")
    op.drop_index("ix_semantic_memories_user_id", table_name="semantic_memories")
    op.drop_table("semantic_memories")
    op.drop_index("ix_diet_logs_log_date", table_name="diet_logs")
    op.drop_index("ix_diet_logs_user_id", table_name="diet_logs")
    op.drop_table("diet_logs")
    op.drop_index("ix_workout_logs_log_date", table_name="workout_logs")
    op.drop_index("ix_workout_logs_user_id", table_name="workout_logs")
    op.drop_table("workout_logs")
    op.drop_index("ix_progress_logs_log_date", table_name="progress_logs")
    op.drop_index("ix_progress_logs_user_id", table_name="progress_logs")
    op.drop_table("progress_logs")
    op.drop_index("ix_streak_checkins_checkin_date", table_name="streak_checkins")
    op.drop_index("ix_streak_checkins_user_id", table_name="streak_checkins")
    op.drop_table("streak_checkins")
    op.drop_index("ix_period_logs_start_date", table_name="period_logs")
    op.drop_index("ix_period_logs_user_id", table_name="period_logs")
    op.drop_table("period_logs")
    op.drop_table("user_profiles")
    op.drop_table("auth_tokens")
    op.drop_table("auth_users")
