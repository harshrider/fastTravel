from sqlalchemy.orm import Session
from datetime import date, time, timedelta
from models import Tour, Package, Transport, Itinerary, create_tour_availability, create_transport_availability, User, Image

def create_safari_world_tour(db: Session):
    # Ensure there is a test user for created_by in packages
    test_user = db.query(User).filter_by(username="testuser").first()
    if not test_user:
        test_user = User(username="testuser", email="testuser@example.com", password_hash="hashedpassword", role="C")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

    # Create the "Safari World" tour if it doesn't exist
    tour = db.query(Tour).filter_by(name="Safari World").first()
    if not tour:
        tour = Tour(
            name="Safari World",
            description="Explore Safari World, a drive-in zoological park divided into Safari and Marine Park sections.",
            price_A=1500.0,  # Default pricing; specific packages will have their own pricing
            price_B=1800.0,
            price_C=2000.0,
            start_time=time(9, 0),
            end_time=time(16, 0),
            max_tickets=100,
            location_url="http://maps.google.com/?q=safari+world+bangkok",
            images=[Image(url='/static/images/safari_world.jpg')]
        )
        db.add(tour)
        db.commit()
        db.refresh(tour)

    # Create Packages and associate them with the tour
    packages_data = [
        {
            "name": "Safari World Only",
            "description": "Access to Safari Park only.",
            "price_A": 1000,
            "price_B": 1200,
            "price_C": 1500
        },
        {
            "name": "Safari World + Lunch",
            "description": "Access to Safari Park with lunch.",
            "price_A": 1500,
            "price_B": 1700,
            "price_C": 2000
        },
        {
            "name": "Safari + Marine Park + Lunch",
            "description": "Full access to Safari and Marine Park with lunch included.",
            "price_A": 2000,
            "price_B": 2200,
            "price_C": 2500
        }
    ]

    # Define itineraries for each package
    itineraries_data = {
        "Safari World Only": [
            {"time": time(9, 0), "description": "Arrival and entry into Safari Park"},
            {"time": time(12, 0), "description": "Lunch break"},
            {"time": time(15, 0), "description": "Safari tour ends"}
        ],
        "Safari World + Lunch": [
            {"time": time(9, 0), "description": "Arrival and entry into Safari Park"},
            {"time": time(12, 0), "description": "Buffet lunch at Safari Restaurant"},
            {"time": time(13, 0), "description": "Continue exploring Safari Park"},
            {"time": time(16, 0), "description": "Safari tour ends"}
        ],
        "Safari + Marine Park + Lunch": [
            {"time": time(9, 0), "description": "Arrival and entry into Safari Park"},
            {"time": time(11, 0), "description": "Transfer to Marine Park"},
            {"time": time(12, 0), "description": "Buffet lunch at Marine Restaurant"},
            {"time": time(13, 0), "description": "Explore Marine Park"},
            {"time": time(16, 0), "description": "Tour ends"}
        ]
    }

    # Create packages and their itineraries
    for package_data in packages_data:
        package = db.query(Package).filter_by(name=package_data["name"]).first()
        if not package:
            package = Package(
                name=package_data["name"],
                description=package_data["description"],
                price_A=package_data["price_A"],
                price_B=package_data["price_B"],
                price_C=package_data["price_C"],
                created_by=test_user.id
            )
            db.add(package)
            db.commit()
            db.refresh(package)

        # Associate package with the tour
        if package not in tour.packages:
            tour.packages.append(package)
        db.commit()

        # Create itineraries for the package
        itinerary_items_data = itineraries_data.get(package.name, [])
        for item_data in itinerary_items_data:
            itinerary_item = Itinerary(
                package_id=package.id,
                time=item_data["time"],
                description=item_data["description"]
            )
            db.add(itinerary_item)
        db.commit()

    # Create Transport Options
    transports_data = [
        {
            "name": "No Transport",
            "description": "Access without transport.",
            "price_A": 0,
            "price_B": 0,
            "price_C": 0,
            "max_seats": 0  # Unlimited if they arrange own transport
        },
        {
            "name": "Private Car",
            "description": "Private car for up to 4 people.",
            "price_A": 3001,
            "price_B": 3201,
            "price_C": 3501,
            "max_seats": 4
        },
        {
            "name": "Small Van",
            "description": "Small van for up to 10 people.",
            "price_A": 5001,
            "price_B": 5201,
            "price_C": 5501,
            "max_seats": 10
        }
    ]

    for transport_data in transports_data:
        transport = db.query(Transport).filter_by(name=transport_data["name"]).first()
        if not transport:
            transport = Transport(
                name=transport_data["name"],
                description=transport_data["description"],
                price_A=transport_data["price_A"],
                price_B=transport_data["price_B"],
                price_C=transport_data["price_C"],
                start_time=time(8, 30),
                end_time=time(17, 0),
                max_seats=transport_data["max_seats"],
                location_url="http://maps.google.com/?q=safari+world+transport"
            )
            db.add(transport)
            db.commit()
            db.refresh(transport)
            tour.transports.append(transport)  # Associate transport with the tour

    db.commit()

    # Create Availability for Next 3 Months Except Mondays
    start_date = date.today()
    end_date = start_date + timedelta(days=90)  # Next 3 months

    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days)):
        if single_date.weekday() != 0:  # Exclude Mondays (0 is Monday)
            create_tour_availability(tour, single_date, single_date, db)

    print("Safari World Tour, Packages, Transports, and Availability created successfully.")

# Usage
if __name__ == "__main__":
    from database import SessionLocal

    db = SessionLocal()
    try:
        create_safari_world_tour(db)
    finally:
        db.close()
