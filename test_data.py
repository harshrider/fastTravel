import psycopg2
from datetime import date, time, timedelta, datetime
from database import get_db


def generate_time_slots(start, end, delta=timedelta(hours=1)):
    """Generate time slots between start and end times"""
    current = datetime.datetime.combine(date.today(), start)
    end = datetime.datetime.combine(date.today(), end)
    while current < end:
        yield current.time()
        current += delta


def create_safari_world_tour():
    with get_db() as conn:
        with conn.cursor() as cursor:
            try:
                # Create test user
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role) 
                    VALUES ('testuser', 'testuser@example.com', 'hashedpassword', 'C')
                    ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email
                    RETURNING id
                """)
                test_user_id = cursor.fetchone()[0]

                # Create Safari World tour
                cursor.execute("""
                    INSERT INTO tours (name, description, price_A, price_B, price_C, 
                    start_time, end_time, max_tickets, location_url)
                    VALUES ('Safari World', 
                            'Explore Safari World park', 
                            1500.0, 1800.0, 2000.0,
                            '09:00:00', '16:00:00',
                            100,
                            'http://maps.google.com/safariworld')
                    ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description
                    RETURNING id
                """)
                tour_id = cursor.fetchone()[0]

                # Create Packages
                packages = [
                    ('Safari World Only', 'Basic access', 1000, 1200, 1500),
                    ('Safari + Lunch', 'With lunch', 1500, 1700, 2000),
                    ('Full Experience', 'Full package', 2000, 2200, 2500)
                ]

                for pkg in packages:
                    cursor.execute("""
                        INSERT INTO packages (name, description, price_A, price_B, price_C, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description
                        RETURNING id
                    """, (*pkg, test_user_id))
                    pkg_id = cursor.fetchone()[0]

                    # Link package to tour
                    cursor.execute("""
                        INSERT INTO tour_packages (tour_id, package_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (tour_id, pkg_id))

                # Create Transports
                transports = [
                    ('Private Car', '4-seater', 3000, 3200, 3500, 4, True, 'Hotel', 'Park'),
                    ('Minivan', '10-seater', 5000, 5200, 5500, 10, True, 'Hotel', 'Park')
                ]

                for trans in transports:
                    cursor.execute("""
                        INSERT INTO transports (name, description, price_A, price_B, price_C,
                                              max_seats, is_transfer_service, pickup_location, dropoff_location,
                                              start_time, end_time, location_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '08:30:00', '17:00:00', 
                                'http://maps.google.com/transport')
                        ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description
                        RETURNING id
                    """, trans)
                    trans_id = cursor.fetchone()[0]

                    # Link transport to tour
                    cursor.execute("""
                        INSERT INTO tour_transports (tour_id, transport_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (tour_id, trans_id))

                # Create availability for next 90 days (excluding Mondays)
                start_date = date.today()
                for day in range(90):
                    current_date = start_date + timedelta(days=day)
                    if current_date.weekday() == 0:  # Skip Mondays
                        continue

                    # Create time slots
                    for slot in generate_time_slots(time(9, 0), time(16, 0)):
                        cursor.execute("""
                            INSERT INTO tour_availabilities 
                            (tour_id, date, time, available_tickets)
                            VALUES (%s, %s, %s, %s)
                        """, (tour_id, current_date, slot, 100))

                conn.commit()
                print("Test data created successfully!")

            except Exception as e:
                conn.rollback()
                print(f"Error creating test data: {str(e)}")
                raise


if __name__ == "__main__":
    create_safari_world_tour()