"""init

Revision ID: cbdfa63891b7
Revises:
Create Date: 2026-07-30 18:57:05.154859

"""

from collections.abc import Sequence

import sqlalchemy as sa  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cbdfa63891b7"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE tickers (
            id SMALLSERIAL PRIMARY KEY,
            name VARCHAR(20) NOT NULL UNIQUE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE price_records (
            id BIGSERIAL PRIMARY KEY,
            ticker_id SMALLINT NOT NULL,
            price NUMERIC(20, 3) NOT NULL,
            timestamp BIGINT NOT NULL,

        CONSTRAINT ticker_fk FOREIGN KEY (ticker_id)
            REFERENCES tickers (id) ON DELETE RESTRICT,

        CONSTRAINT check_price_positive
            CHECK (price > 0),

        CONSTRAINT uq_price_records_ticker_timestamp
            UNIQUE (ticker_id, timestamp)
        )
        """
    )

    op.execute(
        """
            INSERT INTO tickers (name)
            VALUES ('btc_usd'), ('eth_usd')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS price_records")
    op.execute("DROP TABLE IF EXISTS tickers")
