from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(AsyncAttrs, DeclarativeBase, MappedAsDataclass):
    """Базовый класс для всех моделей."""

    __abstract__ = True


class TickerModel(Base):
    """Описание модели для хранения тикеров."""

    __tablename__ = "tickers"

    id: Mapped[int] = mapped_column(
        SmallInteger, primary_key=True, autoincrement=True, init=False
    )
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    price_records: Mapped[list["PriceRecordModel"]] = relationship(
        back_populates="ticker", uselist=True, lazy="selectin", init=False
    )


class PriceRecordModel(Base):
    """Описание модели для хранения цен валют."""

    __tablename__ = "price_records"

    __table_args__ = (
        CheckConstraint(
            "price > 0",
            name="check_price_positive",
        ),
        UniqueConstraint(
            "ticker_id",
            "timestamp",
            name="uq_price_records_ticker_timestamp",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, init=False
    )
    ticker_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("tickers.id", ondelete="RESTRICT"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(20, 3), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)

    ticker: Mapped[TickerModel] = relationship(
        back_populates="price_records", lazy="selectin", init=False
    )
