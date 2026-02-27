"""
Cura3.ai — MongoDB Atlas Connection
Async MongoDB client using Motor driver.
"""
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Global references (initialized on app startup)
client: AsyncIOMotorClient = None
db = None


async def connect_to_mongodb():
    """Connect to MongoDB Atlas on application startup."""
    global client, db
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,  # 5s timeout
            tlsCAFile=certifi.where(),      # Fix SSL on Windows
        )
        # Force a connection check
        await client.admin.command("ping")
        db = client[settings.MONGODB_DB_NAME]

        # Create indexes for performance
        await db.users.create_index("email", unique=True)
        await db.users.create_index("google_id", unique=True)
        await db.reports.create_index("user_id")
        await db.reports.create_index("created_at")
        await db.diagnoses.create_index("user_id")
        await db.diagnoses.create_index("report_id")
        await db.diagnoses.create_index("created_at")
        await db.chat_sessions.create_index("diagnosis_id")
        await db.chat_sessions.create_index("user_id")
        await db.analytics.create_index("event_type")
        await db.analytics.create_index("timestamp")

        print(f"[DB] Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"[DB] WARNING: Could not connect to MongoDB: {e}")
        print(f"[DB] The app will start, but database features won't work.")
        print(f"[DB] Set MONGODB_URI in backend/.env to fix this.")


async def close_mongodb_connection():
    """Close MongoDB connection on application shutdown."""
    global client
    if client:
        client.close()
        print("[DB] MongoDB connection closed.")


def get_database():
    """Get the database instance."""
    return db
