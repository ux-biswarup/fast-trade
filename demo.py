#!/usr/bin/env python3
"""
Fast Trade Demo Script
Demonstrates various features of the fast-trade library
"""

import pandas as pd
import numpy as np
from fast_trade import run_backtest, validate_backtest
from fast_trade.archive.db_helpers import get_kline

def demo_basic_backtest():
    """Demonstrate a basic backtest with sample data"""
    print("=" * 60)
    print("DEMO 1: Basic Backtest with Sample Data")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=200, freq='1h')
    np.random.seed(42)
    
    # Create realistic price data with trend
    base_price = 100
    trend = np.linspace(0, 20, 200)  # Upward trend
    noise = np.random.normal(0, 2, 200)
    prices = base_price + trend + noise
    
    data = {
        'open': prices + np.random.normal(0, 0.5, 200),
        'high': prices + np.abs(np.random.normal(1, 0.5, 200)),
        'low': prices - np.abs(np.random.normal(1, 0.5, 200)),
        'close': prices,
        'volume': np.random.uniform(1000, 10000, 200)
    }
    df = pd.DataFrame(data, index=dates)
    
    # Simple moving average crossover strategy
    strategy = {
        "base_balance": 10000,
        "freq": "1h",
        "start_date": "2024-01-01",
        "comission": 0.001,  # 0.1% commission
        "datapoints": [
            {
                "args": [10],
                "transformer": "sma",
                "name": "sma_fast"
            },
            {
                "args": [30],
                "transformer": "sma",
                "name": "sma_slow"
            },
            {
                "args": [14],
                "transformer": "rsi",
                "name": "rsi"
            }
        ],
        "enter": [
            ["sma_fast", ">", "sma_slow"],
            ["rsi", "<", 70]
        ],
        "exit": [
            ["sma_fast", "<", "sma_slow"]
        ],
        "trailing_stop_loss": 0.02,  # 2% trailing stop
        "exit_on_end": True
    }
    
    print("Strategy:", strategy)
    
    # Validate strategy
    validation = validate_backtest(strategy)
    print(f"\nValidation: {'✅ Valid' if not validation.get('has_error') else '❌ Invalid'}")
    
    # Run backtest
    result = run_backtest(strategy, df=df)
    summary = result["summary"]
    
    print("\nResults:")
    print(f"  Return: {summary.get('return_perc', 0):.2f}%")
    print(f"  Sharpe Ratio: {summary.get('sharpe_ratio', 0):.2f}")
    print(f"  Number of Trades: {summary.get('num_trades', 0)}")
    print(f"  Win Rate: {summary.get('win_perc', 0):.1f}%")
    print(f"  Final Balance: ${summary.get('equity_final', 0):.2f}")
    print(f"  Max Drawdown: {summary.get('max_drawdown_pct', 0):.1f}%")

def demo_advanced_strategy():
    """Demonstrate a more advanced strategy with multiple indicators"""
    print("\n" + "=" * 60)
    print("DEMO 2: Advanced Strategy with Multiple Indicators")
    print("=" * 60)
    
    # Create more complex sample data
    dates = pd.date_range('2024-01-01', periods=500, freq='1h')
    np.random.seed(123)
    
    # Create data with volatility clustering
    returns = np.random.normal(0, 0.02, 500)
    volatility = np.exp(np.random.normal(0, 0.5, 500))
    prices = 100 * np.exp(np.cumsum(returns * volatility))
    
    data = {
        'open': prices * (1 + np.random.normal(0, 0.001, 500)),
        'high': prices * (1 + np.abs(np.random.normal(0.005, 0.002, 500))),
        'low': prices * (1 - np.abs(np.random.normal(0.005, 0.002, 500))),
        'close': prices,
        'volume': np.random.uniform(5000, 50000, 500)
    }
    df = pd.DataFrame(data, index=dates)
    
    # Advanced strategy using multiple indicators
    strategy = {
        "base_balance": 50000,
        "freq": "1h",
        "start_date": "2024-01-01",
        "comission": 0.0005,  # 0.05% commission
        "datapoints": [
            {
                "args": [20],
                "transformer": "ema",
                "name": "ema_20"
            },
            {
                "args": [50],
                "transformer": "ema",
                "name": "ema_50"
            },
            {
                "args": [14],
                "transformer": "rsi",
                "name": "rsi_14"
            },
            {
                "args": [20, 2],
                "transformer": "bbands",
                "name": "bbands"
            },
            {
                "args": [12, 26, 9],
                "transformer": "macd",
                "name": "macd"
            }
        ],
        "enter": [
            ["ema_20", ">", "ema_50"],
            ["rsi_14", ">", 30],
            ["rsi_14", "<", 80],
            ["close", ">", "bbands_bbands_bb_middle"]
        ],
        "exit": [
            ["ema_20", "<", "ema_50"]
        ],
        "any_exit": [
            ["rsi_14", ">", 85],
            ["close", "<", "bbands_bbands_bb_lower"]
        ],
        "trailing_stop_loss": 0.015,
        "exit_on_end": True
    }
    
    print("Advanced Strategy:", strategy)
    
    # Run backtest
    result = run_backtest(strategy, df=df)
    summary = result["summary"]
    
    print("\nAdvanced Strategy Results:")
    print(f"  Return: {summary.get('return_perc', 0):.2f}%")
    print(f"  Sharpe Ratio: {summary.get('sharpe_ratio', 0):.2f}")
    print(f"  Sortino Ratio: {summary.get('risk_metrics', {}).get('sortino_ratio', 0):.2f}")
    print(f"  Number of Trades: {summary.get('num_trades', 0)}")
    print(f"  Win Rate: {summary.get('win_perc', 0):.1f}%")
    print(f"  Profit Factor: {summary.get('trade_quality', {}).get('profit_factor', 0):.2f}")
    print(f"  Final Balance: ${summary.get('equity_final', 0):.2f}")
    print(f"  Max Drawdown: {summary.get('drawdown_metrics', {}).get('max_drawdown_pct', 0):.1f}%")

def demo_strategy_comparison():
    """Compare different strategies"""
    print("\n" + "=" * 60)
    print("DEMO 3: Strategy Comparison")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=300, freq='1h')
    np.random.seed(456)
    
    # Create trending data
    trend = np.linspace(0, 30, 300)
    prices = 100 + trend + np.random.normal(0, 3, 300)
    
    data = {
        'open': prices + np.random.normal(0, 0.5, 300),
        'high': prices + np.abs(np.random.normal(1, 0.5, 300)),
        'low': prices - np.abs(np.random.normal(1, 0.5, 300)),
        'close': prices,
        'volume': np.random.uniform(2000, 20000, 300)
    }
    df = pd.DataFrame(data, index=dates)
    
    strategies = {
        "Buy and Hold": {
            "base_balance": 10000,
            "freq": "1h",
            "start_date": "2024-01-01",
            "comission": 0.001,
            "datapoints": [],
            "enter": [["close", ">", 0]],  # Always true
            "exit": [["close", "<", 0]],   # Never true
            "exit_on_end": True
        },
        "Simple SMA Crossover": {
            "base_balance": 10000,
            "freq": "1h",
            "start_date": "2024-01-01",
            "comission": 0.001,
            "datapoints": [
                {"args": [10], "transformer": "sma", "name": "sma_10"},
                {"args": [30], "transformer": "sma", "name": "sma_30"}
            ],
            "enter": [["sma_10", ">", "sma_30"]],
            "exit": [["sma_10", "<", "sma_30"]],
            "exit_on_end": True
        },
        "RSI Mean Reversion": {
            "base_balance": 10000,
            "freq": "1h",
            "start_date": "2024-01-01",
            "comission": 0.001,
            "datapoints": [
                {"args": [14], "transformer": "rsi", "name": "rsi_14"}
            ],
            "enter": [["rsi_14", "<", 30]],
            "exit": [["rsi_14", ">", 70]],
            "exit_on_end": True
        }
    }
    
    results = {}
    
    for name, strategy in strategies.items():
        print(f"\nTesting {name}...")
        try:
            result = run_backtest(strategy, df=df)
            summary = result["summary"]
            results[name] = {
                "return": summary.get('return_perc', 0),
                "sharpe": summary.get('sharpe_ratio', 0),
                "trades": summary.get('num_trades', 0),
                "win_rate": summary.get('win_perc', 0),
                "final_balance": summary.get('equity_final', 0)
            }
            print(f"  ✅ {name}: {results[name]['return']:.2f}% return, {results[name]['sharpe']:.2f} Sharpe")
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")
    
    # Find best performing strategy
    if results:
        best_strategy = max(results.items(), key=lambda x: x[1]['return'])
        print(f"\n🏆 Best Strategy: {best_strategy[0]} ({best_strategy[1]['return']:.2f}% return)")

if __name__ == "__main__":
    print("🚀 Fast Trade Demo")
    print("This script demonstrates various features of the fast-trade library")
    
    try:
        demo_basic_backtest()
        demo_advanced_strategy()
        demo_strategy_comparison()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("Fast-trade is working perfectly! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc() 