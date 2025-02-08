# models.py
from enum import Enum
from datetime import datetime, timedelta, time, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    role = Column(String(20))

class Tour(Base):
    __tablename__ = 'tours'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(500))
    price_A = Column(Float)
    price_B = Column(Float)
    price_C = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    max_tickets = Column(Integer)
    location_url = Column(String(200))

# Enums remain the same
class UserRoleEnum(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    E = "E"
    O = "O"


class BookingStatusEnum(str, Enum):
    CONFIRMED = "Confirmed"
    PENDING = "Pending"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


# Simple data classes without ORM mappings
class User:
    def __init__(self, id=None, username=None, email=None, password_hash=None, role=UserRoleEnum.A, credit=0.0):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.credit = credit


class Tag:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class Image:
    def __init__(self, id=None, url=None, tour_id=None, transport_id=None, package_id=None):
        self.id = id
        self.url = url
        self.tour_id = tour_id
        self.transport_id = transport_id
        self.package_id = package_id


class Itinerary:
    def __init__(self, id=None, package_id=None, tour_id=None, time=None, description=None):
        self.id = id
        self.package_id = package_id
        self.tour_id = tour_id
        self.time = time
        self.description = description


class Tour:
    def __init__(self, id=None, name=None, description=None, price_A=None, price_B=None, price_C=None,
                 start_time=None, end_time=None, max_tickets=None, location_url=None):
        self.id = id
        self.name = name
        self.description = description
        self.price_A = price_A
        self.price_B = price_B
        self.price_C = price_C
        self.start_time = start_time
        self.end_time = end_time
        self.max_tickets = max_tickets
        self.location_url = location_url


class Transport:
    def __init__(self, id=None, name=None, description=None, price_A=None, price_B=None, price_C=None,
                 start_time=None, end_time=None, max_seats=None, location_url=None,
                 is_transfer_service=False, pickup_location=None, dropoff_location=None):
        self.id = id
        self.name = name
        self.description = description
        self.price_A = price_A
        self.price_B = price_B
        self.price_C = price_C
        self.start_time = start_time
        self.end_time = end_time
        self.max_seats = max_seats
        self.location_url = location_url
        self.is_transfer_service = is_transfer_service
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location


class TourAvailability:
    def __init__(self, id=None, tour_id=None, date=None, time=None, available_tickets=None, is_available=True):
        self.id = id
        self.tour_id = tour_id
        self.date = date
        self.time = time
        self.available_tickets = available_tickets
        self.is_available = is_available


class TransportAvailability:
    def __init__(self, id=None, transport_id=None, date=None, time=None, available_seats=None, is_available=True):
        self.id = id
        self.transport_id = transport_id
        self.date = date
        self.time = time
        self.available_seats = available_seats
        self.is_available = is_available


class Package:
    def __init__(self, id=None, name=None, description=None, price_A=None, price_B=None, price_C=None, created_by=None):
        self.id = id
        self.name = name
        self.description = description
        self.price_A = price_A
        self.price_B = price_B
        self.price_C = price_C
        self.created_by = created_by


class Cart:
    def __init__(self, id=None, user_id=None):
        self.id = id
        self.user_id = user_id


class CartItem:
    def __init__(self, id=None, cart_id=None, tour_id=None, transport_id=None, package_id=None,
                 date=None, time=None, quantity=1, total_price=None):
        self.id = id
        self.cart_id = cart_id
        self.tour_id = tour_id
        self.transport_id = transport_id
        self.package_id = package_id
        self.date = date
        self.time = time
        self.quantity = quantity
        self.total_price = total_price


class Booking:
    def __init__(self, id=None, user_id=None, tour_id=None, transport_id=None, package_id=None,
                 date=None, time=None, quantity=None, total_price=None,
                 booking_date=None, status=BookingStatusEnum.CONFIRMED):
        self.id = id
        self.user_id = user_id
        self.tour_id = tour_id
        self.transport_id = transport_id
        self.package_id = package_id
        self.date = date
        self.time = time
        self.quantity = quantity
        self.total_price = total_price
        self.booking_date = booking_date or datetime.utcnow()
        self.status = status


# Utility functions updated to use database.py
def generate_time_slots(start_time: time, end_time: time, interval_minutes=60):
    slots = []
    current = datetime.combine(date.today(), start_time)
    end = datetime.combine(date.today(), end_time)

    while current <= end - timedelta(minutes=interval_minutes):
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)
    return slots


def create_tour_availability(tour_id: int, start_date: date, end_date: date):
    from database import fetch_results, execute_query

    # Get tour details
    tour_data = fetch_results(
        "SELECT start_time, end_time, max_tickets FROM tours WHERE id = %s",
        (tour_id,)
    )
    if not tour_data:
        raise ValueError("Tour not found")

    start_time = tour_data[0][0]
    end_time = tour_data[0][1]
    max_tickets = tour_data[0][2]

    current_date = start_date
    while current_date <= end_date:
        time_slots = generate_time_slots(start_time, end_time)
        for slot in time_slots:
            execute_query(
                "INSERT INTO tour_availabilities (tour_id, date, time, available_tickets, is_available) "
                "VALUES (%s, %s, %s, %s, %s)",
                (tour_id, current_date, slot, max_tickets, True)
            )
        current_date += timedelta(days=1)


def create_transport_availability(transport_id: int, start_date: date, end_date: date):
    from database import fetch_results, execute_query

    # Get transport details
    transport_data = fetch_results(
        "SELECT start_time, end_time, max_seats FROM transports WHERE id = %s",
        (transport_id,)
    )
    if not transport_data:
        raise ValueError("Transport not found")

    start_time = transport_data[0][0]
    end_time = transport_data[0][1]
    max_seats = transport_data[0][2]

    current_date = start_date
    while current_date <= end_date:
        time_slots = generate_time_slots(start_time, end_time)
        for slot in time_slots:
            execute_query(
                "INSERT INTO transport_availabilities (transport_id, date, time, available_seats, is_available) "
                "VALUES (%s, %s, %s, %s, %s)",
                (transport_id, current_date, slot, max_seats, True)
            )
        current_date += timedelta(days=1)