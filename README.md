# Deltain Trader

A Python application for fetching historical cryptocurrency data from Delta Exchange India API with configurable timeframes.

## 🚀 Features

- **Configurable Timeframes**: Fetch data with multiple resolutions (1m, 5m, 1h, 1d, etc.)
- **Multiple Symbols**: Support for Bitcoin, Ethereum, Solana, and other perpetual futures
- **Smart Rate Limiting**: Handles API rate limits and pagination automatically
- **Data Export**: Saves data to CSV files with proper formatting
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Error Handling**: Robust error handling and retry mechanisms

## 📊 Supported Timeframes

| Resolution | Description |
|------------|-------------|
| 1m | 1 minute candles |
| 3m | 3 minute candles |
| 5m | 5 minute candles |
| 15m | 15 minute candles |
| 30m | 30 minute candles |
| 1h | 1 hour candles |
| 2h | 2 hour candles |
| 4h | 4 hour candles |
| 6h | 6 hour candles |
| 1d | Daily candles |
| 1w | Weekly candles |

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Internet connection for API access

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Deltain-trader.git
   cd Deltain-trader
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Linux/Mac)
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📋 Configuration

The project uses a central configuration file (`config.py`) with the following settings:

### API Settings
- **Base URL**: `https://api.india.delta.exchange`
- **API Version**: v2
- **Rate Limiting**: 5 requests per second

### Data Configuration
- **Default Symbols**: BTCUSD, ETHUSD, SOLUSD
- **Time Zone**: Asia/Kolkata (IST)
- **Default Lookback**: 10 days
- **Default Resolution**: 1 minute candles

### Output Settings
- **Data Directory**: `data/`
- **Log Directory**: `logs/`
- **CSV Format**: `{symbol}_{resolution}_{start_date}_{end_date}.csv`

## 🚀 Usage

### Interactive Mode

Run the main script for interactive resolution selection:

```bash
python main.py
```

The script will:
1. Display available timeframe options
2. Prompt you to select a resolution
3. Fetch data for all configured symbols
4. Save results to CSV files

### Programmatic Usage

```python
from data_fetcher import DeltaExchangeDataFetcher

# Fetch 1-minute data
minute_fetcher = DeltaExchangeDataFetcher(resolution="1m")
minute_data = minute_fetcher.fetch_symbol_data("BTCUSD")

# Fetch hourly data
hourly_fetcher = DeltaExchangeDataFetcher(resolution="1h")
hourly_data = hourly_fetcher.fetch_symbol_data("BTCUSD")

# Fetch multiple symbols
symbols = ["BTCUSD", "ETHUSD", "SOLUSD"]
results = hourly_fetcher.fetch_multiple_symbols(symbols)
```

### Examples

Run the example script to see different usage patterns:

```bash
python examples/timeframe_examples.py
```

## 📁 Project Structure

```
Deltain-trader/
├── config.py              # Configuration settings
├── data_fetcher.py        # Core data fetching functionality
├── main.py                # Interactive script entry point
├── requirements.txt       # Python dependencies
├── README.md              # This documentation
├── data/                  # Directory for saved CSV files
├── logs/                  # Directory for log files
└── examples/              # Example scripts
    └── timeframe_examples.py
```

## 📊 Data Output

### CSV File Format

Each CSV file contains the following columns:
- `symbol`: Trading pair symbol (e.g., BTCUSD)
- `datetime_ist`: Timestamp in IST timezone
- `datetime`: UTC timestamp
- `time`: Unix timestamp
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `price_change`: Price change (close - open)
- `price_change_pct`: Percentage price change

### File Naming Convention

Files are saved with the following format:
- `BTCUSD_1m_20250710_20250720.csv` (1-minute data)
- `ETHUSD_1h_20250710_20250720.csv` (1-hour data)
- `SOLUSD_1d_20250710_20250720.csv` (daily data)

## ⚙️ Configuration Options

### Customize Symbols

Edit `config.py` to add or remove trading pairs:

```python
SYMBOLS = [
    "BTCUSD",    # Bitcoin perpetual
    "ETHUSD",    # Ethereum perpetual
    "SOLUSD",    # Solana perpetual
    "ADAUSD",    # Add Cardano
    "DOTUSD",    # Add Polkadot
]
```

### Adjust Time Range

Change the data collection period:

```python
DAYS_TO_FETCH = 30  # Fetch last 30 days instead of 10
```

### Modify Rate Limiting

Adjust API request frequency:

```python
MAX_REQUESTS_PER_SECOND = 3  # Slower rate limiting
```

## 🔧 Advanced Usage

### Custom Resolution Fetching

```python
from data_fetcher import DeltaExchangeDataFetcher

# Initialize with custom resolution
fetcher = DeltaExchangeDataFetcher(resolution="5m")

# Fetch data for specific symbol
df = fetcher.fetch_symbol_data("BTCUSD")

# Save with custom parameters
from datetime import datetime
fetcher.save_to_csv(df, "BTCUSD", datetime.now(), datetime.now())
```

### Batch Processing

```python
# Process different timeframes for analysis
resolutions = ["1m", "5m", "1h", "1d"]
symbol = "BTCUSD"

for resolution in resolutions:
    fetcher = DeltaExchangeDataFetcher(resolution=resolution)
    data = fetcher.fetch_symbol_data(symbol)
    print(f"{resolution}: {len(data)} records")
```

## 📋 Dependencies

- **requests**: HTTP library for API communication
- **pandas**: Data manipulation and CSV export
- **python-dateutil**: Date handling utilities
- **pytz**: Timezone support
- **python-dotenv**: Environment variable management

## 🐛 Troubleshooting

### Common Issues

1. **No data retrieved**: 
   - Check internet connection
   - Verify symbol names are correct
   - Check Delta Exchange API status

2. **Rate limiting errors**:
   - Increase `REQUEST_DELAY` in config.py
   - Reduce `MAX_REQUESTS_PER_SECOND`

3. **File permission errors**:
   - Ensure write permissions for `data/` and `logs/` directories
   - Run script with appropriate permissions

### Enable Debug Logging

For detailed troubleshooting, modify the logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📜 API Documentation

This project uses the Delta Exchange India API. For complete API documentation, visit:
https://docs.delta.exchange/#introduction

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves significant risk. Always conduct your own research and consider your risk tolerance before making any trading decisions.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the logs in `logs/data_fetcher.log`
3. Open an issue on GitHub with detailed error information

## 🎯 Roadmap

- [ ] Real-time data streaming via WebSocket
- [ ] Technical indicators calculation
- [ ] Data visualization dashboard
- [ ] Database storage support
- [ ] Multiple exchange support
- [ ] Automated trading strategies

---

**Happy Trading! 📈**
