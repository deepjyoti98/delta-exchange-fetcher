#!/usr/bin/env python3
"""
Delta Exchange India Historical Data Fetcher

Fetches minute-by-minute historical data for the last 10 days
and saves it to CSV files.

Updated with latest package versions and enhanced features.
"""

import logging
import argparse
import pandas as pd
from datetime import datetime
import sys
import os
from pathlib import Path

from data_fetcher import DeltaExchangeDataFetcher
from config import SYMBOLS, get_date_range, RESOLUTION_OPTIONS

# Setup comprehensive logging
log_file = Path('logs') / 'data_fetcher.log'
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║             Delta Exchange India Data Fetcher             ║
    ║                     Version 2025.1                       ║
    ║            Enhanced with Configurable Pairs & Timeframes ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("Available Symbols:")
    for symbol in SYMBOLS:
        print(f"  {symbol}")
    print("\nAvailable Resolutions:")
    for res, desc in RESOLUTION_OPTIONS.items():
        print(f"  {res:>4} -> {desc}")
    print("="*70)

def display_summary(results: dict):
    """Display detailed summary of fetch results"""
    print("\n" + "="*70)
    print("📊 FETCH SUMMARY")
    print("="*70)
    
    total_records = 0
    successful_fetches = 0
    
    for symbol, df in results.items():
        record_count = len(df)
        total_records += record_count
        
        if record_count > 0:
            successful_fetches += 1
            min_price = df['low'].min() if 'low' in df.columns else 'N/A'
            max_price = df['high'].max() if 'high' in df.columns else 'N/A'
            total_volume = df['volume'].sum() if 'volume' in df.columns else 'N/A'
            
            status = "✅ Success"
            details = f"Records: {record_count:,} | Price Range: {min_price}-{max_price} | Volume: {total_volume:,.0f}"
        else:
            status = "❌ Failed"
            details = "No data retrieved"
        
        print(f"{symbol:>10}: {status:<10} | {details}")
    
    print("-" * 70)
    print(f"📈 Total Symbols Processed: {len(results)}")
    print(f"✅ Successful Fetches: {successful_fetches}")
    print(f"📊 Total Records: {total_records:,}")
    print(f"💾 Files saved to: '{os.path.abspath('data')}'")
    print("="*70)

def fetch_data_with_resolution(symbols, resolution="1m"):
    """Fetch data for symbols with specified resolution"""
    logger.info(f"Starting data fetch with {RESOLUTION_OPTIONS[resolution]} resolution")
    
    # Initialize fetcher with specified resolution
    fetcher = DeltaExchangeDataFetcher(resolution=resolution)
    
    # Fetch data for all symbols
    results = fetcher.fetch_multiple_symbols(symbols)
    
    return results

def main():
    """Enhanced main function with configurable resolution support"""
    print_banner()
    
    try:
        # Display configuration
        start_timestamp, end_timestamp, start_date, end_date = get_date_range()
        
        print(f"\n🕒 Date Range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 Symbols: {', '.join(SYMBOLS)}")
        print(f"📁 Output Directory: {os.path.abspath('data')}")
        
        # Get user input for resolution
        print(f"\nSelect resolution (default: 1m):")
        for res, desc in RESOLUTION_OPTIONS.items():
            print(f"  {res} - {desc}")
        
        resolution = input("\nEnter resolution (or press Enter for 1m): ").strip() or "1m"
        
        if resolution not in RESOLUTION_OPTIONS:
            print(f"❌ Invalid resolution '{resolution}'. Using default '1m'")
            resolution = "1m"
        
        print(f"🔍 Using Resolution: {RESOLUTION_OPTIONS[resolution]}")
        print(f"⏱️  Estimated Time: ~{len(SYMBOLS) * 2} minutes")
        print("\nStarting data fetch...\n")
        
        # Fetch data with selected resolution
        results = fetch_data_with_resolution(SYMBOLS, resolution)
        
        # Display comprehensive summary
        display_summary(results)
        
        # Check if any data was successfully fetched
        successful_symbols = [symbol for symbol, df in results.items() if not df.empty]
        
        if successful_symbols:
            logger.info(f"✅ Data fetching completed successfully for {len(successful_symbols)} symbols!")
            print(f"\n🎉 Success! {RESOLUTION_OPTIONS[resolution]} data has been saved for: {', '.join(successful_symbols)}")
            print(f"💡 Files are saved with format: SYMBOL_{resolution}_STARTDATE_ENDDATE.csv")
        else:
            logger.error("❌ No data was successfully fetched for any symbol")
            print("\n⚠️  Warning: No data was fetched. Please check your internet connection and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Process interrupted by user")
        print("\n\n🛑 Process interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Fatal error occurred: {e}")
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
    
    print("\n📋 Check the 'logs/data_fetcher.log' file for detailed execution logs.")

if __name__ == "__main__":
    main()
