from app.database.database import SessionLocal, engine, Base
from app.database.models import Portfolio, Holding


def seed_database():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:

        # Prevent duplicate data
        if db.query(Portfolio).count() > 0:
            print("Database already contains portfolio data.")
            return

        # -------------------------
        # Growth Portfolio
        # -------------------------

        growth = Portfolio(
            name="Growth Portfolio"
        )

        growth.holdings = [
            Holding(
                symbol="RELIANCE.NS",
                quantity=20,
                buy_price=2500,
                sector="Energy"
            ),
            Holding(
                symbol="TCS.NS",
                quantity=10,
                buy_price=3200,
                sector="Information Technology"
            ),
            Holding(
                symbol="INFY.NS",
                quantity=15,
                buy_price=1500,
                sector="Information Technology"
            )
        ]

        # -------------------------
        # Balanced Portfolio
        # -------------------------

        balanced = Portfolio(
            name="Balanced Portfolio"
        )

        balanced.holdings = [
            Holding(
                symbol="HDFCBANK.NS",
                quantity=20,
                buy_price=1600,
                sector="Financial Services"
            ),
            Holding(
                symbol="ITC.NS",
                quantity=30,
                buy_price=450,
                sector="Consumer Staples"
            ),
            Holding(
                symbol="TCS.NS",
                quantity=10,
                buy_price=3200,
                sector="Information Technology"
            )
        ]

        # -------------------------
        # Conservative Portfolio
        # -------------------------

        conservative = Portfolio(
            name="Conservative Portfolio"
        )

        conservative.holdings = [
            Holding(
                symbol="ITC.NS",
                quantity=40,
                buy_price=450,
                sector="Consumer Staples"
            ),
            Holding(
                symbol="HDFCBANK.NS",
                quantity=15,
                buy_price=1600,
                sector="Financial Services"
            )
        ]

        db.add_all([
            growth,
            balanced,
            conservative
        ])

        db.commit()

        print("Portfolio data inserted successfully.")

    except Exception as e:

        db.rollback()

        print("Error while seeding database:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_database()