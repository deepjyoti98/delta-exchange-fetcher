#!/usr/bin/env python3
"""
Technical Indicators Calculator for Delta Exchange Data
Uses the popular 'ta' library for accurate RSI-14, SMA-50, and EMA 9-21 crossover calculations
Saves processed data to organized folders

RSI Settings: Upper limit 60, Lower limit 40, Middle 50, Length 14
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Dict
import os

# Import TA-Lib for technical analysis
try:
    import talib
except ImportError:
    print("❌ Error: 'TA-Lib' library not found!")
    print("📦 Please install it using: pip install TA-Lib")
    print("💡 Note: On Windows, you might need to install the wheel from:")
    print("   https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib")
    exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_output_directories(base_dir: str = 'data') -> Dict[str, Path]:
    """
    Create output directories for all technical indicators
    
    Args:
        base_dir: Base data directory
    
    Returns:
        dict: Dictionary of indicator directory paths
    """
    base_path = Path(base_dir)
    dirs = {
        'rsi': base_path / 'RSI',
        'sma': base_path / 'SMA50',
        'ema_cross': base_path / 'EMA_CROSSOVER',
        'atr': base_path / 'ATR',
        'macd': base_path / 'MACD',
        'bbands': base_path / 'BBANDS',
        'vwap': base_path / 'VWAP',
        'obv': base_path / 'OBV',
        'adx': base_path / 'ADX'
    }
    
    # Create directories if they don't exist
    for dir_path in dirs.values():
        dir_path.mkdir(exist_ok=True)
    
    logger.info(f"Created output directories in {base_dir}")
    return dirs

def calculate_rsi(data: pd.DataFrame, periods: int = 14) -> pd.Series:
    """
    Calculate RSI using TA-Lib
    
    Args:
        data: DataFrame with OHLCV data
        periods: RSI period (default: 14)
    
    Returns:
        pandas.Series: RSI values
    """
    return pd.Series(talib.RSI(data['close'].values, timeperiod=periods), index=data.index)

def calculate_sma(data: pd.DataFrame, periods: int = 50) -> pd.Series:
    """
    Calculate SMA using TA-Lib
    """
    return pd.Series(talib.SMA(data['close'].values, timeperiod=periods), index=data.index)

def calculate_ema_crossover(data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate EMA 9-21 crossover using TA-Lib
    """
    ema9 = pd.Series(talib.EMA(data['close'].values, timeperiod=9), index=data.index)
    ema21 = pd.Series(talib.EMA(data['close'].values, timeperiod=21), index=data.index)
    
    crossover = pd.Series(index=data.index, dtype='object')
    for i in range(1, len(ema9)):
        if pd.notna(ema9.iloc[i]) and pd.notna(ema21.iloc[i]) and pd.notna(ema9.iloc[i-1]) and pd.notna(ema21.iloc[i-1]):
            if ema9.iloc[i] > ema21.iloc[i] and ema9.iloc[i-1] <= ema21.iloc[i-1]:
                crossover.iloc[i] = 'Bullish Cross'
            elif ema9.iloc[i] < ema21.iloc[i] and ema9.iloc[i-1] >= ema21.iloc[i-1]:
                crossover.iloc[i] = 'Bearish Cross'
            elif ema9.iloc[i] > ema21.iloc[i]:
                crossover.iloc[i] = 'Bullish'
            elif ema9.iloc[i] < ema21.iloc[i]:
                crossover.iloc[i] = 'Bearish'
            else:
                crossover.iloc[i] = 'Neutral'
        else:
            crossover.iloc[i] = 'No Data'
    
    return ema9, ema21, crossover

def calculate_atr(data: pd.DataFrame, periods: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR) using TA-Lib
    
    Args:
        data: DataFrame with OHLCV data
        periods: ATR period (default: 14)
    
    Returns:
        pandas.Series: ATR values
    """
    return pd.Series(
        talib.ATR(
            data['high'].values,
            data['low'].values,
            data['close'].values,
            timeperiod=periods
        ),
        index=data.index
    )

def calculate_macd(data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD using TA-Lib
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        tuple: (MACD line, Signal line, MACD histogram)
    """
    macd, signal, hist = talib.MACD(
        data['close'].values,
        fastperiod=12,
        slowperiod=26,
        signalperiod=9
    )
    return (pd.Series(macd, index=data.index),
            pd.Series(signal, index=data.index),
            pd.Series(hist, index=data.index))

def calculate_bbands(data: pd.DataFrame, periods: int = 20) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands using TA-Lib
    
    Args:
        data: DataFrame with OHLCV data
        periods: Period for calculation (default: 20)
    
    Returns:
        tuple: (Upper band, Middle band, Lower band)
    """
    upper, middle, lower = talib.BBANDS(
        data['close'].values,
        timeperiod=periods,
        nbdevup=2,
        nbdevdn=2,
        matype=0
    )
    return (pd.Series(upper, index=data.index),
            pd.Series(middle, index=data.index),
            pd.Series(lower, index=data.index))

def calculate_vwap(data: pd.DataFrame) -> pd.Series:
    """
    Calculate VWAP (Volume Weighted Average Price)
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        pandas.Series: VWAP values
    """
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    vwap = (typical_price * data['volume']).cumsum() / data['volume'].cumsum()
    return vwap

def calculate_obv(data: pd.DataFrame) -> pd.Series:
    """
    Calculate On Balance Volume (OBV) using TA-Lib
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        pandas.Series: OBV values
    """
    return pd.Series(talib.OBV(data['close'].values, data['volume'].values), index=data.index)

def calculate_adx(data: pd.DataFrame, periods: int = 14) -> pd.Series:
    """
    Calculate Average Directional Index (ADX) using TA-Lib
    
    Args:
        data: DataFrame with OHLCV data
        periods: Period for calculation (default: 14)
    
    Returns:
        pandas.Series: ADX values
    """
    return pd.Series(
        talib.ADX(
            data['high'].values,
            data['low'].values,
            data['close'].values,
            timeperiod=periods
        ),
        index=data.index
    )

def get_rsi_signal(rsi_value: float, upper_limit: float = 60, lower_limit: float = 40) -> str:
    """
    Get RSI signal based on custom levels
    
    Args:
        rsi_value: Current RSI value
        upper_limit: Overbought threshold (default: 60)
        lower_limit: Oversold threshold (default: 40)
    
    Returns:
        str: Signal ('Overbought', 'Oversold', 'Neutral')
    """
    if pd.isna(rsi_value):
        return 'No Data'
    elif rsi_value >= upper_limit:
        return 'Overbought'
    elif rsi_value <= lower_limit:
        return 'Oversold'
    else:
        return 'Neutral'

def process_csv_file(file_path: Path, dirs: Dict[str, Path]) -> Dict:
    """
    Process a single CSV file and save technical indicator data
    
    Args:
        file_path: Path to the input CSV file
        dirs: Dictionary of output directories for each indicator
    
    Returns:
        dict: Processing statistics
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert datetime column
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Ensure column names match what we need
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Sort by datetime to ensure proper order
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Convert numeric columns to float64 (double) explicitly
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
        
        # Create datasets for each indicator
        base_filename = file_path.stem

        logger.info(f"Calculating indicators for {file_path.name}...")

        # Calculate all indicators first
        df['RSI_14'] = calculate_rsi(df, periods=14)
        df['SMA_50'] = calculate_sma(df, periods=50)
        ema9, ema21, ema_cross_signal = calculate_ema_crossover(df)
        df['EMA_9'], df['EMA_21'], df['EMA_Cross_Signal'] = ema9, ema21, ema_cross_signal
        df['ATR_14'] = calculate_atr(df, periods=14)
        macd, signal, hist = calculate_macd(df)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = macd, signal, hist
        upper, middle, lower = calculate_bbands(df, periods=20)
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = upper, middle, lower
        df['VWAP'] = calculate_vwap(df)
        df['OBV'] = calculate_obv(df)
        df['ADX'] = calculate_adx(df, periods=14)

        logger.info(f"Creating indicator datasets...")

        # RSI dataset
        rsi_data = df[['datetime', 'close', 'RSI_14']].copy()
        rsi_data['RSI_Signal'] = rsi_data['RSI_14'].apply(
            lambda x: get_rsi_signal(x, upper_limit=60, lower_limit=40)
        )
        rsi_data['RSI_Above_50'] = rsi_data['RSI_14'] > 50
        rsi_data['RSI_Momentum'] = rsi_data['RSI_14'].diff()
        rsi_data.to_csv(dirs['rsi'] / f"{base_filename}_RSI14.csv", index=False)
        logger.info(f"✓ RSI dataset saved")

        # SMA dataset
        sma_data = df[['datetime', 'close', 'SMA_50']].copy()
        sma_data['Price_vs_SMA'] = sma_data.apply(
            lambda row: 'Above' if row['close'] > row['SMA_50'] else 'Below' if pd.notna(row['SMA_50']) else 'No Data', axis=1
        )
        sma_data['SMA_Trend'] = sma_data['SMA_50'].diff().apply(
            lambda x: 'Rising' if x > 0 else 'Falling' if x < 0 else 'Flat' if x == 0 else 'No Data'
        )
        sma_data.to_csv(dirs['sma'] / f"{base_filename}_SMA50.csv", index=False)
        logger.info(f"✓ SMA dataset saved")

        # EMA Crossover dataset
        ema_cross_data = df[['datetime', 'close', 'EMA_9', 'EMA_21', 'EMA_Cross_Signal']].copy()
        ema_cross_data['EMA_9_vs_21'] = ema_cross_data.apply(
            lambda row: 'Above' if row['EMA_9'] > row['EMA_21'] else 'Below' if pd.notna(row['EMA_9']) and pd.notna(row['EMA_21']) else 'No Data', axis=1
        )
        ema_cross_data.to_csv(dirs['ema_cross'] / f"{base_filename}_EMA_CROSSOVER.csv", index=False)
        logger.info(f"✓ EMA Crossover dataset saved")

        # ATR dataset
        atr_data = df[['datetime', 'close', 'ATR_14']].copy()
        atr_data.to_csv(dirs['atr'] / f"{base_filename}_ATR14.csv", index=False)
        logger.info(f"✓ ATR dataset saved")

        # MACD dataset
        macd_data = df[['datetime', 'close', 'MACD', 'MACD_Signal', 'MACD_Hist']].copy()
        macd_data['MACD_Cross'] = np.where(macd_data['MACD'] > macd_data['MACD_Signal'], 'Bullish', 'Bearish')
        macd_data.to_csv(dirs['macd'] / f"{base_filename}_MACD.csv", index=False)
        logger.info(f"✓ MACD dataset saved")

        # Bollinger Bands dataset
        bb_data = df[['datetime', 'close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].copy()
        bb_data['BB_Position'] = bb_data.apply(
            lambda row: 'Above' if row['close'] > row['BB_Upper'] else 'Below' if row['close'] < row['BB_Lower'] else 'Inside', axis=1
        )
        bb_data.to_csv(dirs['bbands'] / f"{base_filename}_BBANDS.csv", index=False)
        logger.info(f"✓ Bollinger Bands dataset saved")

        # VWAP dataset
        vwap_data = df[['datetime', 'close', 'VWAP']].copy()
        vwap_data['Price_vs_VWAP'] = vwap_data.apply(
            lambda row: 'Above' if row['close'] > row['VWAP'] else 'Below', axis=1
        )
        vwap_data.to_csv(dirs['vwap'] / f"{base_filename}_VWAP.csv", index=False)
        logger.info(f"✓ VWAP dataset saved")

        # OBV dataset
        obv_data = df[['datetime', 'close', 'OBV']].copy()
        obv_data['OBV_Change'] = obv_data['OBV'].diff().apply(
            lambda x: 'Increasing' if x > 0 else 'Decreasing' if x < 0 else 'Neutral'
        )
        obv_data.to_csv(dirs['obv'] / f"{base_filename}_OBV.csv", index=False)
        logger.info(f"✓ OBV dataset saved")

        # ADX dataset
        adx_data = df[['datetime', 'close', 'ADX']].copy()
        adx_data['Trend_Strength'] = adx_data['ADX'].apply(
            lambda x: 'Strong' if x > 25 else 'Weak'
        )
        adx_data.to_csv(dirs['adx'] / f"{base_filename}_ADX.csv", index=False)
        logger.info(f"✓ ADX dataset saved")

        # Save consolidated dataset with all indicators
        consolidated_dir = Path(dirs['rsi']).parent / 'consolidated'
        consolidated_dir.mkdir(exist_ok=True)
        
        # Create consolidated DataFrame with all data
        consolidated_data = df[['datetime', 'open', 'high', 'low', 'close', 'volume']].copy()
        
        # Add all technical indicators
        consolidated_data['RSI_14'] = df['RSI_14']
        consolidated_data['SMA_50'] = df['SMA_50']
        consolidated_data['EMA_9'] = df['EMA_9']
        consolidated_data['EMA_21'] = df['EMA_21']
        consolidated_data['EMA_Cross_Signal'] = df['EMA_Cross_Signal']
        consolidated_data['ATR_14'] = df['ATR_14']
        consolidated_data['MACD'] = df['MACD']
        consolidated_data['MACD_Signal'] = df['MACD_Signal']
        consolidated_data['MACD_Hist'] = df['MACD_Hist']
        consolidated_data['BB_Upper'] = df['BB_Upper']
        consolidated_data['BB_Middle'] = df['BB_Middle']
        consolidated_data['BB_Lower'] = df['BB_Lower']
        consolidated_data['VWAP'] = df['VWAP']
        consolidated_data['OBV'] = df['OBV']
        consolidated_data['ADX'] = df['ADX']
        
        # Add all signal columns
        consolidated_data['RSI_Signal'] = consolidated_data['RSI_14'].apply(
            lambda x: get_rsi_signal(x, upper_limit=60, lower_limit=40)
        )
        consolidated_data['RSI_Above_50'] = consolidated_data['RSI_14'] > 50
        consolidated_data['RSI_Momentum'] = consolidated_data['RSI_14'].diff()
        
        consolidated_data['Price_vs_SMA'] = consolidated_data.apply(
            lambda row: 'Above' if row['close'] > row['SMA_50'] else 'Below' if pd.notna(row['SMA_50']) else 'No Data',
            axis=1
        )
        
        consolidated_data['SMA_Trend'] = consolidated_data['SMA_50'].diff().apply(
            lambda x: 'Rising' if x > 0 else 'Falling' if x < 0 else 'Flat' if x == 0 else 'No Data'
        )
        
        consolidated_data['EMA_9_vs_21'] = consolidated_data.apply(
            lambda row: 'Above' if row['EMA_9'] > row['EMA_21'] else 'Below' if pd.notna(row['EMA_9']) and pd.notna(row['EMA_21']) else 'No Data',
            axis=1
        )
        
        consolidated_data['MACD_Cross'] = np.where(
            consolidated_data['MACD'] > consolidated_data['MACD_Signal'],
            'Bullish',
            'Bearish'
        )
        
        consolidated_data['BB_Position'] = consolidated_data.apply(
            lambda row: 'Above' if row['close'] > row['BB_Upper']
            else 'Below' if row['close'] < row['BB_Lower']
            else 'Inside',
            axis=1
        )
        
        consolidated_data['Price_vs_VWAP'] = consolidated_data.apply(
            lambda row: 'Above' if row['close'] > row['VWAP'] else 'Below',
            axis=1
        )
        
        consolidated_data['OBV_Change'] = consolidated_data['OBV'].diff().apply(
            lambda x: 'Increasing' if x > 0 else 'Decreasing' if x < 0 else 'Neutral'
        )
        
        consolidated_data['ADX_Strength'] = consolidated_data['ADX'].apply(
            lambda x: 'Strong' if x > 25 else 'Weak'
        )
        
        # Save consolidated file
        consolidated_file = consolidated_dir / f"{base_filename}_ALL_INDICATORS.csv"
        consolidated_data.to_csv(consolidated_file, index=False)
        logger.info(f"✓ Consolidated dataset saved to {consolidated_file.name}")
        
        # Calculate statistics with valid data only
        valid_rsi_data = rsi_data.dropna(subset=['RSI_14'])
        valid_sma_data = sma_data.dropna(subset=['SMA_50'])
        
        # Get latest values for stats
        last_idx = -1
        current_stats = {
            'symbol': base_filename.split('_')[0],
            'file_processed': file_path.name,
            'total_records': len(df),
            'current_price': df['close'].iloc[last_idx],
            'current_rsi': df['RSI_14'].iloc[last_idx],
            'current_sma': df['SMA_50'].iloc[last_idx],
            'current_ema9': df['EMA_9'].iloc[last_idx],
            'current_ema21': df['EMA_21'].iloc[last_idx],
            'current_ema_cross_signal': df['EMA_Cross_Signal'].iloc[last_idx],
            'current_atr': df['ATR_14'].iloc[last_idx],
            'current_macd': df['MACD'].iloc[last_idx],
            'current_macd_signal': df['MACD_Signal'].iloc[last_idx],
            'current_bb_upper': df['BB_Upper'].iloc[last_idx],
            'current_bb_lower': df['BB_Lower'].iloc[last_idx],
            'current_vwap': df['VWAP'].iloc[last_idx],
            'current_adx': df['ADX'].iloc[last_idx],
            'rsi_signal': get_rsi_signal(df['RSI_14'].iloc[last_idx]),
            'macd_signal': 'Bullish' if df['MACD'].iloc[last_idx] > df['MACD_Signal'].iloc[last_idx] else 'Bearish',
            'bb_position': 'Above' if df['close'].iloc[last_idx] > df['BB_Upper'].iloc[last_idx] else 'Below' if df['close'].iloc[last_idx] < df['BB_Lower'].iloc[last_idx] else 'Inside',
            'adx_strength': 'Strong' if df['ADX'].iloc[last_idx] > 25 else 'Weak',
            'files': {
                'rsi': str(dirs['rsi'] / f"{base_filename}_RSI14.csv"),
                'sma': str(dirs['sma'] / f"{base_filename}_SMA50.csv"),
                'ema_cross': str(dirs['ema_cross'] / f"{base_filename}_EMA_CROSSOVER.csv"),
                'atr': str(dirs['atr'] / f"{base_filename}_ATR14.csv"),
                'macd': str(dirs['macd'] / f"{base_filename}_MACD.csv"),
                'bbands': str(dirs['bbands'] / f"{base_filename}_BBANDS.csv"),
                'vwap': str(dirs['vwap'] / f"{base_filename}_VWAP.csv"),
                'obv': str(dirs['obv'] / f"{base_filename}_OBV.csv"),
                'adx': str(dirs['adx'] / f"{base_filename}_ADX.csv"),
                'consolidated': str(consolidated_file)
            }
        }
        
        logger.info(f"✅ Processed {file_path.name} with all indicators")
        logger.info(f"   Price: ${current_stats['current_price']:.2f}")
        logger.info(f"   RSI: {current_stats['current_rsi']:.2f} ({current_stats['rsi_signal']})")
        logger.info(f"   SMA-50: ${current_stats['current_sma']:.2f}")
        logger.info(f"   EMA Cross: {current_stats['current_ema_cross_signal']}")
        logger.info(f"   ADX: {current_stats['current_adx']:.2f} ({current_stats['adx_strength']})")
        logger.info(f"   MACD Signal: {current_stats['macd_signal']}")
        logger.info(f"   BB Position: {current_stats['bb_position']}")
        
        return current_stats
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Error processing {file_path.name}:")
        logger.error(f"   Error details: {str(e)}")
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        
        # Check if file exists and is readable
        if not file_path.exists():
            logger.error(f"   File does not exist: {file_path}")
        else:
            # Try to read the first few lines to check format
            try:
                df_check = pd.read_csv(file_path, nrows=1)
                logger.error(f"   File columns: {df_check.columns.tolist()}")
            except Exception as read_err:
                logger.error(f"   Error reading CSV: {str(read_err)}")
        return None

def process_all_csv_files(data_dir: str = 'data') -> Dict:
    """
    Process all CSV files in the data directory
    
    Args:
        data_dir: Directory containing CSV files (default: 'data')
    
    Returns:
        dict: Processing results for all files
    """
    # Create output directories
    dirs = create_output_directories(data_dir)
    
    data_path = Path(data_dir)
    results = {}
    processed_count = 0
    failed_count = 0
    
    try:
        # Get all CSV files in the main data directory (not subdirectories)
        csv_files = [f for f in data_path.glob('*.csv') if f.is_file()]
        
        if not csv_files:
            logger.warning(f"No CSV files found in {data_dir}")
            return {}
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        # Process each CSV file
        for file_path in csv_files:
            logger.info(f"Processing {file_path.name}...")
            
            stats = process_csv_file(file_path, dirs)
            
            if stats:
                symbol = stats['symbol']
                results[symbol] = stats
                processed_count += 1
            else:
                failed_count += 1
        
        # Log summary
        logger.info(f"\n📊 Processing Summary:")
        logger.info(f"✅ Successfully processed: {processed_count} files")
        logger.info(f"❌ Failed to process: {failed_count} files")
        logger.info(f"📁 Files saved to the following directories:")
        for indicator, dir_path in dirs.items():
            logger.info(f"   � {indicator.upper()}: {dir_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return {}

if __name__ == "__main__":
    # Enhanced batch processing
    print("\n📊 Technical Indicators Batch Processor")
    print("🎯 RSI Settings: Upper=60, Lower=40, Middle=50, Length=14, Smoothing=14")
    print("=" * 70)
    print("🔄 Processing all CSV files and organizing RSI/EMA data...")
    
    # Process all CSV files and save to organized folders
    results = process_all_csv_files()
    
    if results:
        print("\n🔍 Processing Results Summary:")
        print("=" * 70)
        
        for symbol, stats in results.items():
            print(f"\n📈 {symbol}:")
            print(f"  📁 Source: {stats['file_processed']}")
            print(f"  📊 Records: {stats['total_records']:,}")
            print(f"  💰 Current Price: ${stats['current_price']:.2f}")
            print(f"\n  Technical Indicators:")
            print(f"  📈 RSI-14: {stats['current_rsi']:.2f} ({stats['rsi_signal']})")
            print(f"\n  Technical Indicators:")
            print(f"  📈 RSI-14: {stats['current_rsi']:.2f} ({stats['rsi_signal']})")
            print(f"  📊 SMA-50: ${stats['current_sma']:.2f}")
            print(f"  📈 EMA Cross: {stats['current_ema_cross_signal']} (EMA9: ${stats['current_ema9']:.2f}, EMA21: ${stats['current_ema21']:.2f})")
            print(f"  📏 ATR-14: {stats['current_atr']:.2f}")
            print(f"  📊 MACD: {stats['current_macd']:.2f} ({stats['macd_signal']})")
            print(f"  📈 Bollinger Bands: {stats['bb_position']}")
            print(f"      Upper: ${stats['current_bb_upper']:.2f}")
            print(f"      Lower: ${stats['current_bb_lower']:.2f}")
            print(f"  📊 VWAP: ${stats['current_vwap']:.2f}")
            print(f"  📈 ADX: {stats['current_adx']:.2f} ({stats['adx_strength']})")
        
        print(f"\n✅ Successfully processed {len(results)} symbols!")
        print("📁 Check the following directories for output files:")
        print("   📊 RSI data: data/RSI/")
        print("   📈 SMA data: data/SMA50/")
        print("   📈 EMA Crossover data: data/EMA_CROSSOVER/")
        print("   📏 ATR data: data/ATR/")
        print("   📊 MACD data: data/MACD/")
        print("   📈 Bollinger Bands: data/BBANDS/")
        print("   📊 VWAP data: data/VWAP/")
        print("   📈 OBV data: data/OBV/")
        print("   📊 ADX data: data/ADX/")
        print("   📊 Consolidated data: data/consolidated/")
        
    else:
        print("\n⚠️ No files were processed. Please check:")
        print("   1. CSV files exist in the 'data' directory")
        print("   2. CSV files have the correct format (datetime, open, high, low, close, volume)")
        print("   3. File permissions allow reading/writing")
    
    print("\n🎯 Tip: Use the generated CSV files for further analysis or visualization!")
    print("🎯 RSI Settings: Overbought ≥60, Oversold ≤40, Neutral 40-60")

