# test_data.py
from routers.auth import get_password_hash  # Corrected import statement
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import User, Tour, Transport, Cart, CartItem, UserRoleEnum

# Create all tables in the database (in case they haven't been created yet)
Base.metadata.create_all(bind=engine)


# Initialize a new database session
def populate_data():
    db: Session = SessionLocal()

    try:
        # Clear existing data
        db.query(CartItem).delete()
        db.query(Cart).delete()
        db.query(User).delete()
        db.query(Tour).delete()
        db.query(Transport).delete()

        # Create sample users
        user1 = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("1"),
            role=UserRoleEnum.A
        )
        user2 = User(
            username="business",
            email="business@example.com",
            password_hash=get_password_hash("1"),
            role=UserRoleEnum.B
        )
        user3 = User(
            username="customer",
            email="customer@example.com",
            password_hash=get_password_hash("1"),
            role=UserRoleEnum.C
        )

        # Add users to the session and commit
        db.add_all([user1, user2, user3])
        db.commit()  # Commit to get IDs assigned
        db.refresh(user1)
        db.refresh(user2)
        db.refresh(user3)

        # Create sample carts
        cart1 = Cart(user_id=user3.id)
        db.add(cart1)
        db.commit()
        db.refresh(cart1)

        # Create sample tours
        tour1 = Tour(
            name="Bangkok Adventure",
            description="Explore the best of Bangkok in this full-day tour.",
            price_A=1000.0,
            price_B=1200.0,
            price_C=1500.0,
            image_url="static/images/tour1.jpg"
        )

        tour2 = Tour(
            name="Chiang Mai Nature Escape",
            description="Discover the beauty of Chiang Mai's natural landscapes.",
            price_A=1500.0,
            price_B=1800.0,
            price_C=2000.0,
            image_url="static/images/tour2.jpg"
        )

        # Add tours to the session
        db.add_all([tour1, tour2])

        # Create sample transports
        transport1 = Transport(
            name="Van Rental",
            description="Comfortable vans for group travel.",
            price_A=500.0,
            price_B=600.0,
            price_C=700.0,
            image_url="static/images/transport1.jpg"
        )

        transport2 = Transport(
            name="Bike Rental",
            description="Rent bikes to explore at your own pace.",
            price_A=200.0,
            price_B=250.0,
            price_C=300.0,
            image_url="static/images/transport2.jpg"
        )

        # Add transports to the session
        db.add_all([transport1, transport2])

        # Create sample carts
        cart1 = Cart(user_id=user3.id)
        db.add(cart1)
        db.commit()
        db.refresh(cart1)

        # Create sample cart items
        cart_item1 = CartItem(
            cart_id=cart1.id,
            tour_id=tour1.id,
            quantity=2
        )
        cart_item2 = CartItem(
            cart_id=cart1.id,
            transport_id=transport2.id,
            quantity=1
        )

        # Add cart items to the session
        db.add_all([cart_item1, cart_item2])

        # Commit all changes to the database
        db.commit()
        print("Sample data added successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()


# Run the function to populate data
if __name__ == "__main__":
    populate_data()
