import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Load environment variables (optional)
load_dotenv()

# API Configuration
BASE_URL = "https://api.india.delta.exchange"
API_VERSION = "v2"

# Data Configuration
SYMBOLS = [
    "ETHUSD",    # Ethereum perpetual
    # Add more symbols as needed
]

# Time Configuration
IST = pytz.timezone('Asia/Kolkata')
DAYS_TO_FETCH = 10

# Resolution Configuration
# Supported resolutions by Delta Exchange API
RESOLUTION_OPTIONS = {
    "1m": "1 minute",
    "3m": "3 minutes", 
    "5m": "5 minutes",
    "15m": "15 minutes",
    "30m": "30 minutes",
    "1h": "1 hour",
    "2h": "2 hours",
    "4h": "4 hours",
    "6h": "6 hours",
    "1d": "1 day",
    "1w": "1 week"
}

# Default resolution
RESOLUTION = "1m"  # Default to 1 minute candles

# Rate limiting (requests per second) - being conservative for public endpoints
MAX_REQUESTS_PER_SECOND = 5
REQUEST_DELAY = 1 / MAX_REQUESTS_PER_SECOND

# Output Configuration
OUTPUT_DIR = "data"
CSV_FILENAME_FORMAT = "{symbol}_{start_date}_{end_date}.csv"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_date_range():
    """Get start and end dates for the last 10 days"""
    now = datetime.now(IST)
    end_date = now
    start_date = now - timedelta(days=DAYS_TO_FETCH)
    
    # Convert to Unix timestamps (seconds)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    return start_timestamp, end_timestamp, start_date, end_date
