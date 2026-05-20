# Example Prompts v2.0

Copy these prompts into Claude, ChatGPT, Gemini, or another AI with `SKILL.md` loaded.

---

## Basic EA — MA Crossover with Full Risk Management

```text
Using the MQL5 EA Expert skill, create a compile-ready MetaTrader 5 EA for EURUSD H1:
- Fast EMA 10 / Slow EMA 30 crossover entry
- Risk 1% per trade, ATR-based SL (1.5x ATR), TP at 2:1 RR
- Max 1 position at a time
- Break-even at 1R profit, trailing stop after 1.5R
- Daily loss limit 5%, max drawdown 20%, spread filter 30 points
- Day/session filter: Monday–Friday, 7:00–20:00 GMT
- Magic number input, full journal logging
Return one complete .mq5 file plus setup instructions.
```

---

## Multi-Timeframe Trend Pullback

```text
Create a survival-first MQL5 EA using the MQL5 EA Expert skill:
- H4 trend bias: price above/below EMA 50 and EMA 200
- H1 pullback confirmation: RSI 14 between 40–60
- M15 entry trigger: bullish/bearish engulfing candle close
- Risk 0.75% per trade, ATR-based SL (1x ATR on M15)
- TP at 2.5:1 RR, partial close 50% at 1:1
- Max 1 open position per symbol/magic
- Daily loss 4%, max drawdown 15%, spread filter 25 points
- Full logging and error handling
- Prop firm mode: daily DD 4.5%, total DD 9%
```

---

## SMC Order Block + FVG Entry EA

```text
Using the MQL5 EA Expert skill, build an EA for XAUUSD M15:
- Higher timeframe (H1): detect BOS (Break of Structure) for direction bias
- On M15: mark bullish Order Block (last bearish candle before bullish BOS)
- Entry: price returns to OB zone AND closes inside a Bullish FVG
- SL: below OB low + 10 point buffer
- TP: at next swing high / liquidity target (1:2 minimum)
- Risk 1% per trade
- London KZ only: 2:00–5:00 GMT
- Max spread 40 points
- Draw OB and FVG zones on chart with rectangle objects
- Dashboard: show balance, equity, floating PL, active trades
```

---

## ICT Kill Zone + Silver Bullet EA

```text
Create a complete MQL5 EA using the MQL5 EA Expert skill:
Strategy: ICT Silver Bullet (NY AM 10:00–11:00 GMT)
- During Silver Bullet window, identify FVG after liquidity sweep
- Bullish: sweep of Asian low, then bullish FVG forms on M1/M5
- Bearish: sweep of Asian high, then bearish FVG forms on M1/M5
- Entry: limit order placed at FVG midpoint
- SL: 3 points beyond the liquidity sweep candle wick
- TP: 1:2 RR or 50% of the day range
- Risk 0.5% per trade, max 1 trade per Silver Bullet window
- Mark Asian range high/low on chart
- Mark FVG zones with chart objects
- Session filter: only trade during NY AM 10:00–11:00 GMT
- Prop firm safe: daily DD 4%, total DD 8%
Symbol: EURUSD, primary TF: M5
```

---

## CRT (Candle Range Theory) EA

```text
Using the MQL5 EA Expert skill, build a CRT-based EA for GBPUSD H1:
- Reference candle: previous day (Daily timeframe)
- Mark: High, Low, Equilibrium (50%), +1SD, -1SD, +2SD, -2SD levels
- Manipulation phase: price sweeps beyond the daily High or Low (wick)
- Displacement confirmation: strong candle closing back inside range on H1
- Buy setup: sweep of daily Low -> displacement close above Eq -> long entry
- Sell setup: sweep of daily High -> displacement close below Eq -> short entry
- SL: 10 points beyond the manipulation wick extreme
- TP: opposing SD level (e.g. entry near -1SD -> TP at +1SD)
- Risk 1% per trade
- Trade only London and NY sessions (2:00–17:00 GMT)
- Draw CRT levels as horizontal lines on chart, label each level
- Max spread 30 points, max 1 trade per day
- Full prop firm protection: daily DD 5%, total DD 10%
```

---

## Asian Range Breakout EA

```text
Create an Asian Range Breakout EA using the MQL5 EA Expert skill:
- Calculate Asian session range: 00:00–02:00 GMT (High and Low)
- Draw horizontal lines at Asian High and Asian Low on chart
- Entry on London open (02:00 GMT): breakout above Asian High = BUY, 
  breakout below Asian Low = SELL
- Breakout confirmation: candle close outside range, not just wick
- SL: inside the range (50% of Asian range from entry)
- TP: 1.5x the Asian range extension
- Risk 1% per trade, max 1 trade per day
- Only trade Monday–Thursday (skip Friday)
- Max spread 20 points at entry
- ATR filter: only trade if ATR > 50 points (avoid low volatility days)
- Dashboard showing today's Asian High/Low and trade status
Symbol: EURUSD, TF: M15
```

---

## Safe Grid EA (Ranging Market)

```text
Create an educational safe-grid MQL5 EA using the MQL5 EA Expert skill:
- Grid step: 50 points between levels
- Max grid levels: 5 (hard cap, no exceptions)
- Lot multiplier: 1.0 only (no martingale escalation)
- Grid direction: based on M15 EMA 50 bias (buy grid above EMA, sell grid below)
- Emergency shutdown: if drawdown > 15% close all and halt
- Basket profit target: $50 (configurable input)
- Reset: after basket closes, recalculate EMA bias before starting new grid
- Max spread: 25 points before placing any grid level
- Full logging of each grid level open/close
Include explicit risk warning in comments and a note that this is demo-only.
```

---

## Custom Indicator — SMC Structure + OB + FVG

```text
Using the MQL5 EA Expert skill, create a custom indicator for MetaTrader 5:
- Detects and draws: Bullish BOS, Bearish BOS, CHoCH (Change of Character)
- Marks Order Blocks: last bearish candle before bullish BOS (blue rectangle),
  last bullish candle before bearish BOS (red rectangle)
- Marks FVGs: bullish FVG (green fill) and bearish FVG (red fill) using 3-candle pattern
- All objects prefixed with "SMC_" for easy cleanup
- Inputs: lookback period for swing detection, OB/FVG opacity, colors
- Label each structure break on chart with text objects
- Indicator window: below chart, plots Structure Signal buffer
  (1 = Bullish BOS, -1 = Bearish BOS, 0 = none)
- MT5 alerts when new BOS or CHoCH detected
Symbol: works on any symbol/timeframe
```

---

## Backtest Validator Class

```text
Create an MQL5 utility class using the MQL5 EA Expert skill that validates
backtest results from the account history:
- Calculate: profit factor, win rate, max drawdown, recovery factor,
  simplified Sharpe ratio, win/loss ratio
- Generate acceptance report with PASS/FAIL thresholds:
  PF >= 1.5, DD <= 20%, RF >= 3, trades >= 50
- Filter deals by symbol and magic number
- Include PrintReport() method for MT5 Journal output
- Include IsStrategyAcceptable() bool method
- Include OnTester() function returning composite score
```
