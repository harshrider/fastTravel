# populate_test_data.py
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import User, Tour, TourAvailability, UserRoleEnum
from datetime import datetime, timedelta

# Create all tables in the database (in case they haven't been created yet)
Base.metadata.create_all(bind=engine)


# Initialize a new database session
def populate_data():
    db: Session = SessionLocal()

    try:
        # Clear existing data
        db.query(User).delete()
        db.query(Tour).delete()
        db.query(TourAvailability).delete()

        # Create sample users
        user1 = User(username="user1", email="user1@example.com", password_hash="hashed_password1", role=UserRoleEnum.A,
                     credit=100.0)
        user2 = User(username="user2", email="user2@example.com", password_hash="hashed_password2", role=UserRoleEnum.B,
                     credit=200.0)
        user3 = User(username="user3", email="user3@example.com", password_hash="hashed_password3", role=UserRoleEnum.C,
                     credit=300.0)

        # Add users to the session
        db.add_all([user1, user2, user3])

        # Create sample tours
        tour1 = Tour(
            name="Bangkok Adventure",
            description="Explore the best of Bangkok in this full-day tour.",
            price_A=1000.0,
            price_B=1200.0,
            price_C=1500.0,
            image_url="static/images/tour1.jpg",
            available_time_start=datetime.strptime("08:00", "%H:%M").time(),
            available_time_end=datetime.strptime("18:00", "%H:%M").time(),
            phone_number="1234567890",
            email="tour@example.com",
            location="Bangkok",
            days="Monday, Wednesday, Friday",
            itinerary="Morning city tour, afternoon river cruise.",
            tags="adventure,city",
            map="https://maps.example.com/bangkok_adventure"
        )

        tour2 = Tour(
            name="Chiang Mai Nature Escape",
            description="Discover the beauty of Chiang Mai's natural landscapes.",
            price_A=1500.0,
            price_B=1800.0,
            price_C=2000.0,
            image_url="static/images/tour2.jpg",
            available_time_start=datetime.strptime("09:00", "%H:%M").time(),
            available_time_end=datetime.strptime("17:00", "%H:%M").time(),
            phone_number="0987654321",
            email="tour2@example.com",
            location="Chiang Mai",
            days="Tuesday, Thursday, Saturday",
            itinerary="Mountain trekking, elephant sanctuary visit.",
            tags="nature,relaxation",
            map="https://maps.example.com/chiang_mai_nature"
        )

        # Add tours to the session
        db.add_all([tour1, tour2])

        # Create sample tour availability
        tour_availability1 = TourAvailability(
            tour_id=1,
            date=datetime.now(),
            status="available",
            stock=20
        )

        tour_availability2 = TourAvailability(
            tour_id=2,
            date=datetime.now() + timedelta(days=1),
            status="available",
            stock=15
        )

        # Add tour availability to the session
        db.add_all([tour_availability1, tour_availability2])

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
