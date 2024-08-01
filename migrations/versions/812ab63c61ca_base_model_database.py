"""base model database

Revision ID: 812ab63c61ca
Revises: 
Create Date: 2024-08-01 14:27:37.044184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from constants import target, enum


# revision identifiers, used by Alembic.
revision: str = '812ab63c61ca'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(255), unique=True),
        sa.Column("password", sa.String(255)),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("role", sa.Enum(*enum.User_Role), default=target.USER),
    )
    op.create_table(
        "category",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255)),
    )
    op.create_table(
        "book",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255)),
        sa.Column("author", sa.String(255)),
        sa.Column("category", sa.Integer, sa.ForeignKey("category.id")),
        sa.Column("publishing_company", sa.String(255)),
        sa.Column("publication_date", sa.DateTime),
        sa.Column("available_quantity", sa.Integer),
        sa.Column("describe", sa.String(255), nullable=True),
    )
    op.create_table(
        "borrow",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer),
        sa.Column("book_id", sa.Integer),
        sa.Column("borrow_date", sa.DateTime),
        sa.Column("expected_payment_date", sa.DateTime),
        sa.Column("actual_payment_date", sa.DateTime, nullable=True),
        sa.Column("status", sa.Enum(*enum.Borrow_status), default=target.BORROW),
    )


def downgrade() -> None:
    op.drop_table("borrow")
    op.drop_table("book")
    op.drop_table("category")
    op.drop_table("user")
