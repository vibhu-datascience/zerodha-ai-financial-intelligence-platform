from app.database.database import SessionLocal
from app.database.models import User, Portfolio, Holding
from app.services.auth_service import AuthService


def seed_database():

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # GET OR CREATE DEMO USER
        # -------------------------------------------------

        demo_user = (
            db.query(User)
            .filter(
                User.username == "demo_user1"
            )
            .first()
        )

        if not demo_user:

            auth_service = AuthService()

            demo_user = User(
                username="demo_user1",
                password_hash=auth_service.hash_password(
                    "Demo@12345"
                )
            )

            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            print("Demo user created.")

        # -------------------------------------------------
        # GET OR CREATE GROWTH PORTFOLIO
        # -------------------------------------------------

        growth = (
            db.query(Portfolio)
            .filter(
                Portfolio.user_id == demo_user.id
            )
            .first()
        )

        if growth:

            print(
                "Database already contains portfolio data."
            )

            return

        # -------------------------------------------------
        # CREATE GROWTH PORTFOLIO
        # -------------------------------------------------

        growth = Portfolio(
            user_id=demo_user.id,
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

        db.add(growth)

        db.commit()

        print(
            "Demo portfolio created successfully."
        )

    except Exception as e:

        db.rollback()

        print(
            "Error while seeding database:"
        )

        print(e)

    finally:

        db.close()


if __name__ == "__main__":

    seed_database()