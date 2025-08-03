#!/usr/bin/env python3
"""
Simple test script to demonstrate fast-trade functionality
"""

import pandas as pd
import numpy as np
from fast_trade import run_backtest, validate_backtest

# Create sample data
dates = pd.date_range('2024-01-01', periods=100, freq='1H')
np.random.seed(42)
data = {
    'open': np.random.uniform(100, 110, 100),
    'high': np.random.uniform(110, 120, 100),
    'low': np.random.uniform(90, 100, 100),
    'close': np.random.uniform(100, 110, 100),
    'volume': np.random.uniform(1000, 10000, 100)
}
df = pd.DataFrame(data, index=dates)

# Simple strategy
strategy = {
    "base_balance": 1000,
    "freq": "1H",
    "start_date": "2024-01-01",
    "comission": 0.01,
    "datapoints": [
        {
            "args": [20],
            "transformer": "sma",
            "name": "sma_short"
        },
        {
            "args": [50],
            "transformer": "sma", 
            "name": "sma_long"
        }
    ],
    "enter": [
        ["close", ">", "sma_long"],
        ["close", ">", "sma_short"]
    ],
    "exit": [
        ["close", "<", "sma_short"]
    ],
    "trailing_stop_loss": 0.05,
    "exit_on_end": True
}

print("Testing fast-trade with sample data...")
print("Strategy:", strategy)

# Validate the strategy
print("\nValidating strategy...")
validation = validate_backtest(strategy)
print("Validation result:", validation)

# Run the backtest
print("\nRunning backtest...")
result = run_backtest(strategy, df=df)

print("\nBacktest Results:")
print("=" * 50)
summary = result["summary"]
print(f"Return: {summary.get('return_perc', 'N/A'):.2f}%")
print(f"Sharpe Ratio: {summary.get('sharpe_ratio', 'N/A'):.2f}")
print(f"Number of Trades: {summary.get('num_trades', 'N/A')}")
print(f"Win Percentage: {summary.get('win_perc', 'N/A'):.2f}%")
print(f"Final Balance: ${summary.get('equity_final', 'N/A'):.2f}")

print("\nFast-trade is working! 🎉") 