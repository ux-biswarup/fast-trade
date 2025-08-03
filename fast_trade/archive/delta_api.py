#!/usr/bin/env python3
"""
Delta Exchange India API Implementation
Handles data retrieval from Delta Exchange India API
"""

import datetime
import math
import os
import random
import time
from typing import Optional, Callable

import pandas as pd
import requests

# Delta Exchange India API Configuration
DELTA_API_BASE_URL = "https://api.india.delta.exchange"
API_DELAY = float(os.getenv("DELTA_API_DELAY", 0.3))

# Rate limiting configuration
RATE_LIMIT_QUOTA = 10000  # 10,000 requests per 5-minute window
RATE_LIMIT_WINDOW = 300   # 5 minutes in seconds

# Supported timeframes
SUPPORTED_TIMEFRAMES = [
    "1m", "3m", "5m", "15m", "30m",  # minutes
    "1h", "2h", "4h", "6h", "12h",   # hours
    "1d", "3d",                      # days
    "1w",                            # week
    "1M"                             # month
]

# OHLCV data structure mapping
DELTA_KLINE_HEADER_MATCH = [
    "time",      # Unix timestamp in seconds
    "open",       # Open price
    "high",       # High price
    "low",        # Low price
    "close",      # Close price
    "volume",     # Volume
]


def get_exchange_info() -> dict:
    """
    Get Delta Exchange India exchange information
    
    Returns:
        dict: Exchange information including available products
    """
    url = f"{DELTA_API_BASE_URL}/v2/products"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            return data.get("result", {})
        else:
            print(f"Error getting exchange info: {data.get('error', {})}")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting exchange info: {e}")
        return {}


def get_available_symbols() -> list:
    """
    Get list of available trading symbols from Delta Exchange India
    
    Returns:
        list: List of available symbol strings
    """
    exchange_info = get_exchange_info()
    symbols = []
    
    # Parse products to extract symbols
    for product in exchange_info:
        if product.get("state") == "live":
            symbol = product.get("symbol")
            if symbol:
                symbols.append(symbol)
    
    symbols.sort()
    return symbols


def get_oldest_date_available(symbol: str) -> datetime.datetime:
    """
    Get the oldest available date for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSD")
        
    Returns:
        datetime: Oldest available date (defaults to 1 year ago)
    """
    # For Delta Exchange, we'll use a reasonable default
    # since there's no specific endpoint for oldest date
    return datetime.datetime.utcnow() - datetime.timedelta(days=365)


def get_delta_klines(
    symbol: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    resolution: str = "1m",
    status_update: Callable = lambda x: None,
    store_func: Callable = lambda x, y: None,
) -> tuple:
    """
    Download OHLCV data from Delta Exchange India
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSD")
        start_date: Start date for data
        end_date: End date for data
        resolution: Time resolution (1m, 5m, 1h, etc.)
        status_update: Callback for progress updates
        store_func: Callback for storing data
        
    Returns:
        tuple: (DataFrame, status_object)
    """
    start_date = start_date.replace(tzinfo=datetime.timezone.utc)
    end_date = end_date.replace(tzinfo=datetime.timezone.utc)
    
    # Validate resolution
    if resolution not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"Unsupported resolution: {resolution}. Supported: {SUPPORTED_TIMEFRAMES}")
    
    curr_date = start_date
    
    # Delta API can return up to 2000 candles per request
    # We'll use 1000 to be safe and account for rate limits
    CANDLES_PER_REQUEST = 1000
    
    # Calculate time increment based on resolution
    resolution_minutes = _resolution_to_minutes(resolution)
    time_increment = datetime.timedelta(minutes=resolution_minutes * CANDLES_PER_REQUEST)
    
    # Ensure end_date doesn't exceed current time
    now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    if end_date > now:
        end_date = now.replace(second=0, microsecond=0)
    
    # Calculate estimated API calls
    total_duration_minutes = (end_date - curr_date).total_seconds() / 60
    num_calls = math.ceil(total_duration_minutes / (resolution_minutes * CANDLES_PER_REQUEST))
    total_api_calls = 0
    klines = []
    start_time = time.time()
    
    while curr_date < end_date:
        next_end_date = curr_date + time_increment
        if next_end_date > end_date:
            next_end_date = end_date
        
        # Convert to Unix timestamp (seconds)
        start_timestamp = int(curr_date.timestamp())
        end_timestamp = int(next_end_date.timestamp())
        
        print(f"Getting {symbol} from {curr_date} to {next_end_date}")
        
        # Delta Exchange candles endpoint
        url = f"{DELTA_API_BASE_URL}/v2/history/candles"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "start": start_timestamp,
            "end": end_timestamp,
            "limit": CANDLES_PER_REQUEST
        }
        
        try:
            req = requests.get(url, params=params)
            total_api_calls += 1
            error_count = 0
            
            if req.status_code == 200:
                data = req.json()
                
                if data.get("success"):
                    candles = data.get("result", [])
                    klines.extend(candles)
                    curr_date = next_end_date
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    print(f"API Error: {error_msg}")
                    error_count += 1
                    
            elif req.status_code == 429:
                # Rate limit exceeded
                reset_time = req.headers.get("X-RATE-LIMIT-RESET")
                if reset_time:
                    wait_time = int(reset_time) - int(time.time())
                    if wait_time > 0:
                        print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                else:
                    print("Rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                continue
                
            else:
                print(f"HTTP Error {req.status_code}: {req.text}")
                error_count += 1
                
            if error_count > 3:
                raise Exception(f"Download failed for {symbol} after 3 errors")
                
        except Exception as e:
            print(f"Error downloading {symbol}: {e}")
            break
        
        # Rate limiting - respect Delta's rate limits
        sleeper = random.random() * API_DELAY
        if sleeper < 0.1:
            sleeper += 0.1
        
        # Periodic data storage
        if total_api_calls % 30 == 0:
            sleeper += random.randint(1, 3)
            kline_df = delta_kline_to_df(klines)
            store_func(kline_df, symbol, "delta")
        
        # Status update
        status_obj = {
            "symbol": symbol,
            "perc_complete": round(total_api_calls / num_calls * 100, 2),
            "call_count": total_api_calls,
            "total_calls": num_calls,
            "total_time": round(time.time() - start_time, 2),
            "est_time_remaining": round(
                (time.time() - start_time)
                / total_api_calls
                * (num_calls - total_api_calls),
                2,
            ),
        }
        status_update(status_obj)
        time.sleep(sleeper)
    
    # Final status update
    status_obj = {
        "symbol": symbol,
        "perc_complete": 100,
        "call_count": total_api_calls,
        "total_calls": total_api_calls,
        "total_time": time.time() - start_time,
        "est_time_remaining": 0,
    }
    status_update(status_obj)
    
    klines_df = delta_kline_to_df(klines)
    return klines_df, status_obj


def delta_kline_to_df(klines: list) -> pd.DataFrame:
    """
    Convert Delta Exchange kline data to pandas DataFrame
    
    Args:
        klines: List of kline data from Delta API
        
    Returns:
        pd.DataFrame: Formatted OHLCV data
    """
    if not klines:
        return pd.DataFrame()
    
    # Convert to DataFrame
    new_df = pd.DataFrame(klines, columns=DELTA_KLINE_HEADER_MATCH)
    
    # Remove duplicates
    new_df = new_df.drop_duplicates()
    
    # Convert timestamp from microseconds to datetime
    new_df.index = pd.to_datetime(new_df.time, unit='s')
    
    # Drop the timestamp column since it's now the index
    new_df = new_df.drop(columns=['time'])
    
    # Sort by timestamp
    new_df = new_df.sort_index()
    
    return new_df


def _resolution_to_minutes(resolution: str) -> int:
    """
    Convert resolution string to minutes
    
    Args:
        resolution: Resolution string (1m, 5m, 1h, etc.)
        
    Returns:
        int: Minutes
    """
    resolution_map = {
        "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
        "1h": 60, "2h": 120, "4h": 240, "6h": 360, "12h": 720,
        "1d": 1440, "3d": 4320,
        "1w": 10080,  # 7 days
        "1M": 43200   # 30 days (approximate)
    }
    
    return resolution_map.get(resolution, 1)


# Legacy function names for compatibility
def get_exchange_info_delta():
    """Legacy function name"""
    return get_exchange_info()


def get_available_symbols_delta():
    """Legacy function name"""
    return get_available_symbols()


def get_delta_klines_legacy(
    symbol,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    status_update=lambda x: None,
    store_func=lambda x, y: None,
):
    """Legacy function name"""
    return get_delta_klines(symbol, start_date, end_date, status_update=status_update, store_func=store_func)


def delta_kline_to_df_legacy(klines):
    """Legacy function name"""
    return delta_kline_to_df(klines)
