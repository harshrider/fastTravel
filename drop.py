from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Tour, Transport, Package, Tag
from datetime import time

# Define your database URL
DATABASE_URL = "postgresql://gg:Z5yt1FihCSOdyuO6kQQCvVaSOJTLL6ur@dpg-cskcdibtq21c73dm0jr0-a.singapore-postgres.render.com/dbtravel_58nj"

# Set up the engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def drop_tables_except_users():
    # Create metadata and reflect the tables
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # List of table names to exclude from dropping
    exclude_tables = [User.__tablename__]  # Keeps the 'users' table

    # Drop dependent tables first
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # Drop tables except those listed in exclude_tables
            for table in reversed(metadata.sorted_tables):
                if table.name not in exclude_tables:
                    print(f"Dropping table: {table.name} (with CASCADE)")
                    connection.execute(text(f"DROP TABLE {table.name} CASCADE"))
            transaction.commit()
            print("All tables dropped except 'users'.")
        except Exception as e:
            transaction.rollback()
            print(f"Error dropping tables: {e}")

def create_tables():
    # Create all tables defined in Base
    print("Creating tables...")
    # Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def add_test_data():
    # Open a session to add test data
    db = SessionLocal()
    try:
        # Add test users (if not already in the database)
        test_user = User(username="testuser", email="testuser@example.com", password_hash="hashedpassword", role="C")
        db.add(test_user)

        # Add a test tour
        test_tour = Tour(
            name="Safari Adventure",
            description="A thrilling safari tour.",
            price_A=5000,
            price_B=4500,
            price_C=4000,
            start_time=time(9, 0),
            end_time=time(17, 0),
            max_tickets=100,
            location_url="https://example.com/safari"
        )
        db.add(test_tour)

        # Add a test transport
        test_transport = Transport(
            name="Private Van",
            description="A private van for comfortable travel.",
            price_A=3000,
            price_B=2800,
            price_C=2500,
            start_time=time(8, 0),
            end_time=time(20, 0),
            max_seats=10,
            pickup_location="Bangkok",
            dropoff_location="Safari Park"
        )
        db.add(test_transport)

        # Add a test package
        test_package = Package(
            name="Full Day Safari Experience",
            description="Includes access to all areas and lunch.",
            price_A=7500,
            price_B=7000,
            price_C=6500,
            created_by=test_user.id
        )
        db.add(test_package)

        # Add a test tag
        test_tag = Tag(name="Adventure")
        db.add(test_tag)

        db.commit()
        print("Test data added successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error adding test data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    drop_tables_except_users()
    create_tables()
    add_test_data()
