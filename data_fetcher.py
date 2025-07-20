import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import warnings

from config import (
    BASE_URL, API_VERSION, RESOLUTION, REQUEST_DELAY,
    OUTPUT_DIR, CSV_FILENAME_FORMAT, get_date_range, IST,
    RESOLUTION_OPTIONS
)

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeltaExchangeDataFetcher:
    def __init__(self, resolution: str = RESOLUTION):
        """
        Initialize the data fetcher with configurable resolution
        
        Args:
            resolution: Time resolution for candles (1m, 5m, 1h, 1d, etc.)
                       Must be one of the supported resolutions in RESOLUTION_OPTIONS
        """
        if resolution not in RESOLUTION_OPTIONS:
            available = ", ".join(RESOLUTION_OPTIONS.keys())
            raise ValueError(f"Invalid resolution '{resolution}'. Available options: {available}")
        
        self.base_url = BASE_URL
        self.resolution = resolution
        self.session = requests.Session()
        # Simplified headers for public endpoints
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'python-historical-data-fetcher/2025.1'
        })
        
        logger.info(f"Initialized data fetcher with {RESOLUTION_OPTIONS[resolution]} resolution")

    def fetch_candles_batch(self, symbol: str, start: int, end: int) -> Optional[List[Dict]]:
        """
        Fetch a batch of candles for a given symbol and time range
        Max 2000 candles per request
        """
        url = f"{self.base_url}/{API_VERSION}/history/candles"
        
        params = {
            'resolution': self.resolution,
            'symbol': symbol,
            'start': start,
            'end': end
        }
        
        try:
            logger.info(f"Fetching {symbol} {RESOLUTION_OPTIONS[self.resolution]} data from {start} to {end}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success', False):
                result = data.get('result', [])
                logger.info(f"Successfully fetched {len(result)} {RESOLUTION_OPTIONS[self.resolution]} candles for {symbol}")
                return result
            else:
                logger.error(f"API returned error for {symbol}: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {symbol}: {e}")
            return None

    def _calculate_batch_duration(self) -> int:
        """Calculate optimal batch duration based on resolution to stay under 2000 candle limit"""
        resolution_minutes = {
            "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "2h": 120, "4h": 240, "6h": 360,
            "1d": 1440, "1w": 10080
        }
        
        minutes_per_candle = resolution_minutes.get(self.resolution, 1)
        max_candles = 1800  # Stay safely under 2000 limit
        
        # Calculate days that give us ~1800 candles
        total_minutes = max_candles * minutes_per_candle
        days = total_minutes / (24 * 60)
        
        # Ensure minimum of 1 day, maximum reasonable based on resolution
        if self.resolution in ["1m", "3m", "5m"]:
            days = min(max(days, 1), 5)  # 1-5 days for minute data
        elif self.resolution in ["15m", "30m", "1h"]:
            days = min(max(days, 7), 30)  # 1-4 weeks for hourly data
        else:
            days = min(max(days, 30), 365)  # 1-12 months for daily data
        
        return int(days * 24 * 60 * 60)  # Convert to seconds

    def fetch_all_candles(self, symbol: str, start_timestamp: int, end_timestamp: int) -> List[Dict]:
        """
        Fetch all candles for a symbol, handling pagination due to 2000 candle limit
        """
        all_candles = []
        current_start = start_timestamp
        
        # Calculate batch size dynamically based on resolution
        batch_duration = self._calculate_batch_duration()
        
        logger.info(f"Using batch duration of {batch_duration // (24*60*60)} days for {RESOLUTION_OPTIONS[self.resolution]} resolution")
        
        while current_start < end_timestamp:
            current_end = min(current_start + batch_duration, end_timestamp)
            
            batch_candles = self.fetch_candles_batch(symbol, current_start, current_end)
            
            if batch_candles:
                all_candles.extend(batch_candles)
                logger.info(f"Total {RESOLUTION_OPTIONS[self.resolution]} candles collected for {symbol}: {len(all_candles)}")
            else:
                logger.warning(f"No data received for {symbol} batch")
            
            current_start = current_end + 1
            
            # Rate limiting for public endpoints
            time.sleep(REQUEST_DELAY)
        
        logger.info(f"Completed fetching {len(all_candles)} total {RESOLUTION_OPTIONS[self.resolution]} candles for {symbol}")
        return all_candles

    def candles_to_dataframe(self, candles: List[Dict], symbol: str) -> pd.DataFrame:
        """Convert candles data to pandas DataFrame with enhanced data types"""
        if not candles:
            logger.warning(f"No candles data to convert for {symbol}")
            return pd.DataFrame()
        
        df = pd.DataFrame(candles)
        
        # Convert timestamp to readable datetime
        df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
        df['datetime_ist'] = df['datetime'].dt.tz_convert(IST)
        
        # Add symbol column
        df['symbol'] = symbol
        
        # Ensure proper data types
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Reorder columns for better readability
        columns = ['symbol', 'datetime_ist', 'datetime', 'time', 'open', 'high', 'low', 'close', 'volume']
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]
        
        # Sort by time and reset index
        df = df.sort_values('time').reset_index(drop=True)
        
        # Add data quality metrics
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = (df['price_change'] / df['open'] * 100).round(4)
        
        logger.info(f"Created DataFrame for {symbol} with {len(df)} rows and {len(df.columns)} columns")
        return df

    def save_to_csv(self, df: pd.DataFrame, symbol: str, start_date: datetime, end_date: datetime):
        """Save DataFrame to CSV file with metadata"""
        if df.empty:
            logger.warning(f"No data to save for {symbol}")
            return
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        # Include resolution in filename
        filename = f"{symbol}_{self.resolution}_{start_str}_{end_str}.csv"
        filepath = f"{OUTPUT_DIR}/{filename}"
        
        # Save with optimized settings
        df.to_csv(filepath, 
                 index=False, 
                 float_format='%.8f',
                 date_format='%Y-%m-%d %H:%M:%S')
        
        # Log file statistics
        file_size = os.path.getsize(filepath) / 1024  # Size in KB
        logger.info(f"Saved {len(df)} {RESOLUTION_OPTIONS[self.resolution]} records to {filepath} ({file_size:.2f} KB)")

    def fetch_symbol_data(self, symbol: str) -> pd.DataFrame:
        """Fetch all data for a single symbol with enhanced error handling"""
        start_timestamp, end_timestamp, start_date, end_date = get_date_range()
        
        logger.info(f"Starting data fetch for {symbol} from {start_date} to {end_date}")
        
        try:
            candles = self.fetch_all_candles(symbol, start_timestamp, end_timestamp)
            
            if not candles:
                logger.error(f"No data fetched for {symbol}")
                return pd.DataFrame()
            
            df = self.candles_to_dataframe(candles, symbol)
            
            if not df.empty:
                self.save_to_csv(df, symbol, start_date, end_date)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return pd.DataFrame()

    def fetch_multiple_symbols(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols with progress tracking"""
        results = {}
        total_symbols = len(symbols)
        
        logger.info(f"Starting batch fetch for {total_symbols} symbols using {RESOLUTION_OPTIONS[self.resolution]} resolution (No authentication required)")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"Processing symbol {i}/{total_symbols}: {symbol}")
                df = self.fetch_symbol_data(symbol)
                results[symbol] = df
                
                # Progress update
                if not df.empty:
                    logger.info(f"✅ {symbol}: {len(df)} {RESOLUTION_OPTIONS[self.resolution]} records fetched successfully")
                else:
                    logger.warning(f"⚠️  {symbol}: No data retrieved")
                
                # Brief pause between symbols
                if i < total_symbols:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Failed to fetch data for {symbol}: {e}")
                results[symbol] = pd.DataFrame()
        
        return results

    def __del__(self):
        """Clean up session on object destruction"""
        if hasattr(self, 'session'):
            self.session.close()
