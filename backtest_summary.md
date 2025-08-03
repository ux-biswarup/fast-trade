# Backtest Results Summary - strategy.json

## Strategy Overview
- **Strategy Type**: ZLEMA (Zero-Lag Exponential Moving Average) Crossover
- **Symbol**: BTCUSDT
- **Exchange**: Binance.US
- **Timeframe**: 5-minute candles
- **Test Period**: July 4, 2025 - August 3, 2025 (30 days)
- **Starting Balance**: $1,000

## Strategy Logic
- **Entry**: When 9-period ZLEMA > Close price (confirmed for 4 periods)
- **Exit**: When 99-period ZLEMA < Close price (confirmed for 2 periods)
- **Commission**: 1% per trade
- **Trailing Stop**: None

## Performance Results

### 📈 **Overall Performance**
- **Total Return**: +6.13%
- **Final Balance**: $1,065.27
- **Peak Balance**: $1,079.73
- **Buy & Hold Return**: +4.01%
- **Market Outperformance**: +2.12%

### 📊 **Risk Metrics**
- **Sharpe Ratio**: 0.95 (Good risk-adjusted returns)
- **Sortino Ratio**: 0.01
- **Maximum Drawdown**: -3.93%
- **Current Drawdown**: -1.37%
- **Annualized Volatility**: 1.2%

### 🎯 **Trading Statistics**
- **Total Trades**: 357
- **Winning Trades**: 82 (23.0%)
- **Losing Trades**: 275 (77.0%)
- **Win Rate**: 22.97%
- **Average Win**: +0.073%
- **Average Loss**: -0.02%
- **Profit Factor**: 1.07

### ⏱️ **Trade Analysis**
- **Average Trade Duration**: 19.9 minutes
- **Longest Trade**: 655 minutes
- **Shortest Trade**: 5 minutes
- **Time in Market**: 41.2%
- **Total Commission Paid**: $18.68

### 📉 **Drawdown Analysis**
- **Max Drawdown Duration**: 2,751 minutes (~46 hours)
- **Average Drawdown**: -0.99%
- **Current Streak**: 275 losing trades

### 📅 **Time-Based Performance**
- **Best Day**: +2.77%
- **Worst Day**: -1.81%
- **Profitable Days**: 67.7%
- **Average Daily Return**: +0.26%

## Strategy Analysis

### ✅ **Strengths**
1. **Positive Returns**: Strategy outperformed buy & hold
2. **Good Sharpe Ratio**: 0.95 indicates decent risk-adjusted returns
3. **Low Maximum Drawdown**: Only -3.93% maximum loss
4. **High Trading Frequency**: 357 trades in 30 days shows active strategy

### ⚠️ **Areas of Concern**
1. **Low Win Rate**: Only 22.97% of trades are profitable
2. **Long Losing Streak**: Currently on 275 consecutive losing trades
3. **High Commission Impact**: 1.75% of returns lost to fees
4. **Small Average Wins**: +0.073% vs -0.02% losses

### 🔧 **Potential Improvements**
1. **Add Stop Loss**: Implement trailing stop to limit losses
2. **Filter Signals**: Add additional indicators to improve win rate
3. **Reduce Commission**: Consider lower-fee exchanges
4. **Position Sizing**: Implement dynamic position sizing based on volatility

## Recommendations

### 🟢 **Keep Strategy If:**
- You're comfortable with high-frequency trading
- You can handle the current drawdown
- You want to optimize the entry/exit conditions

### 🔴 **Consider Modifications If:**
- You need higher win rates
- You want to reduce trading frequency
- You're concerned about the long losing streak

### 🟡 **Next Steps:**
1. **Parameter Optimization**: Test different ZLEMA periods
2. **Add Filters**: Include RSI, volume, or volatility filters
3. **Risk Management**: Implement stop losses and position sizing
4. **Timeframe Testing**: Test on different timeframes (1H, 4H, 1D)

## Technical Details
- **Data Points**: 8,641 total price ticks
- **Missing Data**: 0% (complete dataset)
- **Test Duration**: 0.195 seconds (very fast execution)
- **Rules Passed**: All strategy rules were satisfied

---
*Backtest completed on: August 3, 2025*
*Strategy: ZLEMA Crossover on BTCUSDT* 