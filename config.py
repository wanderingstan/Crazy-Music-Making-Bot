import os
import dotenv

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


# Check if TOKEN is valid
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set or empty.")

# Check if REPLICATE_API_TOKEN is valid
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN environment variable is not set or empty.")

# Check if ACTIVE_CHANNEL_ID is valid
ACTIVE_CHANNEL_ID = os.getenv("ACTIVE_CHANNEL_ID")
if not ACTIVE_CHANNEL_ID:
    raise ValueError("ACTIVE_CHANNEL_ID environment variable is not set or empty.")

# For testing, shoudl we return fake results instead of calling the API?
DO_FAKE_RESULTS = os.getenv("DO_FAKE_RESULTS", "FALSE").upper() == "TRUE"


TEMP_PATH = os.getenv("TEMP_PATH", "temp_files/")
if not os.path.exists(TEMP_PATH):
    raise ValueError(
        f"TEMP_PATH variable points to non existant directory: {TEMP_PATH}"
    )
