"""
Database seed script.
Populates the GlobeTrotter database with dummy data (users, cities,
activities, trips, stops, itinerary activities, and community posts) so
the frontend has something to render during development/demos.

Usage:
    python seed.py            # seed the database
    python seed.py --reset    # drop all tables, recreate schema, then seed
"""
import sys
from datetime import date, timedelta, time

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import (
    User, City, Activity, Trip, Stop, ItineraryActivity,
    CommunityPost, CommunityComment, CommunityLike, SavedDestination,
)

app = create_app()


def seed():
    with app.app_context():
        if "--reset" in sys.argv:
            print("Dropping all tables...")
            db.drop_all()

        print("Creating tables...")
        db.create_all()

        if User.query.first():
            print("Database already contains data. Skipping seed. Use --reset to start fresh.")
            return

        # --- Users ---
        print("Seeding users...")
        admin = User(
            username="admin",
            email="admin@globetrotter.com",
            first_name="Ava",
            last_name="Admin",
            city="San Francisco",
            country="USA",
            is_admin=True,
        )
        admin.set_password("Admin@123")

        alice = User(
            username="alice",
            email="alice@example.com",
            first_name="Alice",
            last_name="Nguyen",
            city="New York",
            country="USA",
        )
        alice.set_password("Password@123")

        bob = User(
            username="bob",
            email="bob@example.com",
            first_name="Bob",
            last_name="Smith",
            city="London",
            country="UK",
        )
        bob.set_password("Password@123")

        db.session.add_all([admin, alice, bob])
        db.session.commit()

        # --- Cities ---
        print("Seeding cities...")
        cities_data = [
            ("Paris", "France", "Europe", 8.5, 98, 48.8566, 2.3522),
            ("Tokyo", "Japan", "Asia", 7.5, 95, 35.6762, 139.6503),
            ("Rome", "Italy", "Europe", 7.0, 90, 41.9028, 12.4964),
            ("Bali", "Indonesia", "Asia", 4.0, 88, -8.3405, 115.0920),
            ("New York", "USA", "North America", 9.0, 93, 40.7128, -74.0060),
            ("Barcelona", "Spain", "Europe", 6.5, 85, 41.3851, 2.1734),
            ("Bangkok", "Thailand", "Asia", 3.5, 82, 13.7563, 100.5018),
            ("Cape Town", "South Africa", "Africa", 5.0, 78, -33.9249, 18.4241),
            ("Sydney", "Australia", "Oceania", 8.0, 80, -33.8688, 151.2093),
            ("Dubai", "UAE", "Middle East", 8.8, 84, 25.2048, 55.2708),
        ]
        cities = []
        for name, country, region, cost_index, popularity, lat, lng in cities_data:
            city = City(
                name=name, country=country, region=region,
                description=f"{name} is a top destination in {region}.",
                image_url=f"https://source.unsplash.com/featured/?{name.replace(' ', '')}",
                cost_index=cost_index, popularity=popularity, latitude=lat, longitude=lng,
            )
            cities.append(city)
        db.session.add_all(cities)
        db.session.commit()

        city_by_name = {c.name: c for c in cities}

        # --- Activities ---
        print("Seeding activities...")
        activities_data = [
            ("Eiffel Tower Visit", "Paris", "sightseeing", 30, 120, 4.8),
            ("Seine River Cruise", "Paris", "sightseeing", 20, 90, 4.5),
            ("Louvre Museum Tour", "Paris", "culture", 25, 180, 4.7),
            ("Shibuya Crossing Walk", "Tokyo", "sightseeing", 0, 30, 4.4),
            ("Sushi Making Class", "Tokyo", "food", 60, 120, 4.9),
            ("TeamLab Digital Art Museum", "Tokyo", "culture", 35, 150, 4.8),
            ("Colosseum Guided Tour", "Rome", "culture", 40, 120, 4.7),
            ("Italian Pasta Cooking Class", "Rome", "food", 55, 150, 4.8),
            ("Beach Surfing Lesson", "Bali", "adventure", 45, 120, 4.6),
            ("Ubud Rice Terrace Trek", "Bali", "adventure", 25, 180, 4.7),
            ("Statue of Liberty Ferry", "New York", "sightseeing", 25, 150, 4.5),
            ("Broadway Show", "New York", "culture", 120, 180, 4.9),
            ("Sagrada Familia Tour", "Barcelona", "culture", 30, 90, 4.8),
            ("Tapas Food Tour", "Barcelona", "food", 50, 150, 4.7),
            ("Grand Palace Visit", "Bangkok", "sightseeing", 15, 120, 4.5),
            ("Street Food Night Tour", "Bangkok", "food", 30, 150, 4.8),
            ("Table Mountain Cable Car", "Cape Town", "adventure", 35, 90, 4.6),
            ("Safari Day Trip", "Cape Town", "adventure", 150, 480, 4.9),
            ("Sydney Opera House Tour", "Sydney", "culture", 42, 90, 4.7),
            ("Desert Safari", "Dubai", "adventure", 80, 240, 4.8),
        ]
        activities = []
        for name, city_name, category, cost, duration, rating in activities_data:
            activities.append(
                Activity(
                    city_id=city_by_name[city_name].id,
                    name=name, description=f"Enjoy {name} in {city_name}.",
                    category=category, cost=cost, duration_minutes=duration,
                    rating=rating, image_url=f"https://source.unsplash.com/featured/?{name.replace(' ', '')}",
                )
            )
        db.session.add_all(activities)
        db.session.commit()

        # --- Trips for Alice ---
        print("Seeding trips, stops and itinerary activities...")
        today = date.today()

        trip1 = Trip(
            user_id=alice.id,
            name="European Adventure",
            description="A whirlwind tour through Paris, Rome and Barcelona.",
            start_date=today + timedelta(days=20),
            end_date=today + timedelta(days=30),
        )
        trip2 = Trip(
            user_id=alice.id,
            name="Southeast Asia Getaway",
            description="Relaxing on the beaches of Bali and exploring Bangkok.",
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=3),
        )
        trip3 = Trip(
            user_id=alice.id,
            name="NYC Weekend",
            description="A quick trip back home to New York.",
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=57),
        )
        db.session.add_all([trip1, trip2, trip3])
        db.session.commit()

        def make_stop(trip, city_name, start_offset, duration_days, order_index):
            stop = Stop(
                trip_id=trip.id,
                city_id=city_by_name[city_name].id,
                start_date=trip.start_date + timedelta(days=start_offset),
                end_date=trip.start_date + timedelta(days=start_offset + duration_days - 1),
                order_index=order_index,
            )
            db.session.add(stop)
            db.session.commit()
            return stop

        def add_activity_to_stop(stop, activity_name, day_number, day_offset, start_hour):
            activity = Activity.query.filter_by(name=activity_name).first()
            entry = ItineraryActivity(
                stop_id=stop.id,
                activity_id=activity.id,
                day_number=day_number,
                date=stop.start_date + timedelta(days=day_offset),
                start_time=time(hour=start_hour),
                cost=activity.cost,
            )
            db.session.add(entry)

        # Trip 1: Europe
        paris_stop = make_stop(trip1, "Paris", 0, 4, 0)
        rome_stop = make_stop(trip1, "Rome", 4, 3, 1)
        barcelona_stop = make_stop(trip1, "Barcelona", 7, 4, 2)
        add_activity_to_stop(paris_stop, "Eiffel Tower Visit", 1, 0, 9)
        add_activity_to_stop(paris_stop, "Seine River Cruise", 1, 0, 15)
        add_activity_to_stop(paris_stop, "Louvre Museum Tour", 2, 1, 10)
        add_activity_to_stop(rome_stop, "Colosseum Guided Tour", 1, 0, 9)
        add_activity_to_stop(rome_stop, "Italian Pasta Cooking Class", 2, 1, 18)
        add_activity_to_stop(barcelona_stop, "Sagrada Familia Tour", 1, 0, 10)
        add_activity_to_stop(barcelona_stop, "Tapas Food Tour", 1, 0, 19)

        # Trip 2: Southeast Asia
        bali_stop = make_stop(trip2, "Bali", 0, 5, 0)
        bangkok_stop = make_stop(trip2, "Bangkok", 5, 3, 1)
        add_activity_to_stop(bali_stop, "Beach Surfing Lesson", 1, 0, 9)
        add_activity_to_stop(bali_stop, "Ubud Rice Terrace Trek", 2, 1, 8)
        add_activity_to_stop(bangkok_stop, "Grand Palace Visit", 1, 0, 10)
        add_activity_to_stop(bangkok_stop, "Street Food Night Tour", 1, 0, 18)

        # Trip 3: NYC
        nyc_stop = make_stop(trip3, "New York", 0, 4, 0)
        add_activity_to_stop(nyc_stop, "Statue of Liberty Ferry", 1, 0, 10)
        add_activity_to_stop(nyc_stop, "Broadway Show", 2, 1, 19)

        db.session.commit()

        # --- Saved destinations ---
        db.session.add_all(
            [
                SavedDestination(user_id=alice.id, city_id=city_by_name["Tokyo"].id),
                SavedDestination(user_id=alice.id, city_id=city_by_name["Dubai"].id),
                SavedDestination(user_id=bob.id, city_id=city_by_name["Sydney"].id),
            ]
        )
        db.session.commit()

        # --- Community posts ---
        print("Seeding community posts...")
        post1 = CommunityPost(
            user_id=alice.id, trip_id=trip1.id, category="Europe",
            content="Just booked our European Adventure through Paris, Rome and Barcelona - so excited!",
        )
        post2 = CommunityPost(
            user_id=bob.id, category="Asia",
            content="Does anyone have tips for the best street food spots in Bangkok?",
        )
        db.session.add_all([post1, post2])
        db.session.commit()

        db.session.add_all(
            [
                CommunityComment(post_id=post1.id, user_id=bob.id, content="Sounds amazing, have a great trip!"),
                CommunityLike(post_id=post1.id, user_id=bob.id),
                CommunityLike(post_id=post2.id, user_id=alice.id),
            ]
        )
        db.session.commit()

        print("\nSeed complete!")
        print("  Admin login:  username=admin  password=Admin@123")
        print("  User login:   username=alice  password=Password@123")
        print("  User login:   username=bob    password=Password@123")


if __name__ == "__main__":
    seed()
