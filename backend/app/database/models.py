from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    portfolios = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Portfolio(Base):

    __tablename__ = "portfolios"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "name",
            name="uq_portfolio_user_name"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="portfolios"
    )

    holdings = relationship(
        "Holding",
        back_populates="portfolio",
        cascade="all, delete-orphan"
    )


class Holding(Base):

    __tablename__ = "holdings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    portfolio_id = Column(
        Integer,
        ForeignKey("portfolios.id"),
        nullable=False
    )

    symbol = Column(
        String,
        nullable=False
    )

    quantity = Column(
        Float,
        nullable=False
    )

    buy_price = Column(
        Float,
        nullable=False
    )

    sector = Column(
        String,
        nullable=True
    )

    portfolio = relationship(
        "Portfolio",
        back_populates="holdings"
    )