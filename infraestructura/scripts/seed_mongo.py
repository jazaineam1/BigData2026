from datetime import datetime, timezone
import os

from pymongo import ASCENDING, DESCENDING, GEOSPHERE, MongoClient
from pymongo.errors import ServerSelectionTimeoutError


DEFAULT_URIS = [
    "mongodb://admin:admin123@localhost:27017/?authSource=admin",
    "mongodb://admin:admin123@mongo:27017/?authSource=admin",
]
SEED_MARK = "curso_bigdata2026"


def connect() -> MongoClient:
    uris = [os.environ["MONGODB_URI"]] if os.environ.get("MONGODB_URI") else DEFAULT_URIS
    last_error = None
    for uri in uris:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            print("Conexion activa para seed:", uri.split("@")[-1])
            return client
        except ServerSelectionTimeoutError as exc:
            last_error = exc
    raise RuntimeError(f"No se pudo conectar a MongoDB para seed: {last_error}")


def main() -> None:
    client = connect()

    db = client["bigdata_course"]

    restaurants = [
        {
            "name": "Brunos On The Boulevard",
            "borough": "Queens",
            "cuisine": "American",
            "address": {
                "street": "Astoria Boulevard",
                "zipcode": "11369",
                "coord": [-73.8803827, 40.7643124],
            },
            "location": {"type": "Point", "coordinates": [-73.8803827, 40.7643124]},
            "grades": [
                {"date": datetime(2024, 11, 15, tzinfo=timezone.utc), "grade": "A", "score": 10},
                {"date": datetime(2025, 5, 20, tzinfo=timezone.utc), "grade": "B", "score": 22},
            ],
        },
        {
            "name": "La Esquina",
            "borough": "Manhattan",
            "cuisine": "Mexican",
            "address": {
                "street": "Kenmare Street",
                "zipcode": "10012",
                "coord": [-73.9974, 40.7216],
            },
            "location": {"type": "Point", "coordinates": [-73.9974, 40.7216]},
            "grades": [
                {"date": datetime(2025, 1, 9, tzinfo=timezone.utc), "grade": "A", "score": 8},
                {"date": datetime(2025, 8, 9, tzinfo=timezone.utc), "grade": "A", "score": 7},
            ],
        },
        {
            "name": "Bogota Coffee Lab",
            "borough": "Brooklyn",
            "cuisine": "Colombian",
            "address": {
                "street": "Bogart Street",
                "zipcode": "11206",
                "coord": [-73.9341, 40.7051],
            },
            "location": {"type": "Point", "coordinates": [-73.9341, 40.7051]},
            "grades": [
                {"date": datetime(2024, 9, 1, tzinfo=timezone.utc), "grade": "A", "score": 5},
                {"date": datetime(2025, 2, 1, tzinfo=timezone.utc), "grade": "A", "score": 6},
            ],
        },
        {
            "name": "Queens Dumpling House",
            "borough": "Queens",
            "cuisine": "Chinese",
            "address": {
                "street": "Main Street",
                "zipcode": "11354",
                "coord": [-73.8303, 40.7590],
            },
            "location": {"type": "Point", "coordinates": [-73.8303, 40.7590]},
            "grades": [
                {"date": datetime(2023, 6, 1, tzinfo=timezone.utc), "grade": "B", "score": 21},
                {"date": datetime(2025, 3, 1, tzinfo=timezone.utc), "grade": "A", "score": 11},
            ],
        },
    ]

    movies = [
        {
            "title": "The Matrix",
            "year": 1999,
            "genres": ["Action", "Sci-Fi"],
            "runtime": 136,
            "imdb": {"rating": 8.7, "votes": 2100000},
            "languages": ["English"],
            "plot": "A hacker discovers a simulated reality and joins a rebellion.",
        },
        {
            "title": "Roma",
            "year": 2018,
            "genres": ["Drama"],
            "runtime": 135,
            "imdb": {"rating": 7.7, "votes": 180000},
            "languages": ["Spanish", "Mixtec"],
            "plot": "A domestic worker observes family and social change in Mexico City.",
        },
        {
            "title": "Arrival",
            "year": 2016,
            "genres": ["Drama", "Sci-Fi"],
            "runtime": 116,
            "imdb": {"rating": 7.9, "votes": 760000},
            "languages": ["English"],
            "plot": "A linguist works with the military to communicate with alien visitors.",
        },
        {
            "title": "Monsters, Inc.",
            "year": 2001,
            "genres": ["Animation", "Comedy"],
            "runtime": 92,
            "imdb": {"rating": 8.1, "votes": 1000000},
            "languages": ["English"],
            "plot": "Two monsters learn that laughter is more powerful than fear.",
        },
    ]

    weather = [
        {
            "timestamp": datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
            "metaField": {"sensorId": "BOG-001", "city": "Bogota"},
            "temperature": 13.2,
            "humidity": 82,
        },
        {
            "timestamp": datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
            "metaField": {"sensorId": "BOG-001", "city": "Bogota"},
            "temperature": 14.1,
            "humidity": 78,
        },
        {
            "timestamp": datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
            "metaField": {"sensorId": "MED-001", "city": "Medellin"},
            "temperature": 22.4,
            "humidity": 65,
        },
        {
            "timestamp": datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
            "metaField": {"sensorId": "MED-001", "city": "Medellin"},
            "temperature": 23.3,
            "humidity": 62,
        },
    ]

    transactions = [
        {
            "customer_id": 1001,
            "account_id": "A-1001",
            "date": datetime(2026, 1, 3, tzinfo=timezone.utc),
            "amount": 125.50,
            "transaction_code": "buy",
            "symbol": "MDB",
        },
        {
            "customer_id": 1001,
            "account_id": "A-1001",
            "date": datetime(2026, 1, 8, tzinfo=timezone.utc),
            "amount": 80.20,
            "transaction_code": "sell",
            "symbol": "MDB",
        },
        {
            "customer_id": 1002,
            "account_id": "A-1002",
            "date": datetime(2026, 1, 9, tzinfo=timezone.utc),
            "amount": 220.00,
            "transaction_code": "buy",
            "symbol": "AAPL",
        },
    ]

    collections = {
        "restaurants": restaurants,
        "movies": movies,
        "weather_measurements": weather,
        "transactions_demo": transactions,
    }

    for name, documents in collections.items():
        collection = db[name]
        collection.delete_many({"_seed": SEED_MARK})
        docs = [{**doc, "_seed": SEED_MARK} for doc in documents]
        collection.insert_many(docs)

    db.restaurants.create_index([("borough", ASCENDING), ("cuisine", ASCENDING)])
    db.restaurants.create_index([("location", GEOSPHERE)])
    db.movies.create_index([("genres", ASCENDING), ("year", DESCENDING)])
    db.weather_measurements.create_index([("metaField.sensorId", ASCENDING), ("timestamp", ASCENDING)])
    db.transactions_demo.create_index([("customer_id", ASCENDING), ("date", ASCENDING)])

    print("Seed completado en bigdata_course")
    for name in collections:
        print(name, db[name].count_documents({"_seed": SEED_MARK}))


if __name__ == "__main__":
    main()
