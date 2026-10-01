"""add user portfolio relationship

Revision ID: 405172b14653
Revises: 192816adbd1e
Create Date: 2026-09-28 12:45:20.690517

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "405172b14653"

down_revision: Union[str, Sequence[str], None] = "192816adbd1e"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # -------------------------------------------------
    # Add user_id to portfolios
    # -------------------------------------------------

    op.add_column(
        "portfolios",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        )
    )

    # -------------------------------------------------
    # Remove old global portfolio-name uniqueness
    # -------------------------------------------------

    op.drop_constraint(
        "portfolios_name_key",
        "portfolios",
        type_="unique"
    )

    # -------------------------------------------------
    # Allow same portfolio name for different users
    # -------------------------------------------------

    op.create_unique_constraint(
        "uq_portfolio_user_name",
        "portfolios",
        ["user_id", "name"]
    )

    # -------------------------------------------------
    # Connect Portfolio → User
    # -------------------------------------------------

    op.create_foreign_key(
        "fk_portfolios_user_id_users",
        "portfolios",
        "users",
        ["user_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove foreign key
    op.drop_constraint(
        "fk_portfolios_user_id_users",
        "portfolios",
        type_="foreignkey"
    )

    # Remove user/name unique constraint
    op.drop_constraint(
        "uq_portfolio_user_name",
        "portfolios",
        type_="unique"
    )

    # Restore global portfolio-name uniqueness
    op.create_unique_constraint(
        "portfolios_name_key",
        "portfolios",
        ["name"],
        postgresql_nulls_not_distinct=False
    )

    # Remove user_id
    op.drop_column(
        "portfolios",
        "user_id"
    )