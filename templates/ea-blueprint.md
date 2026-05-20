# MQL5 Expert Advisor Output Blueprint v2.0

Use this blueprint when an AI generates a production-ready `.mq5` Expert Advisor.

---

## Response Header (Required Every Time)
- Restate strategy, symbol/timeframe assumptions, risk profile.
- Warn if grid, martingale, high leverage, unrealistic target, or missing SL requested.
- State output is educational and must be backtested/demo-tested before live use.

---

## Required Input Groups (in this order)

```mql5
input group "=== STRATEGY SETTINGS ==="
input group "=== MONEY MANAGEMENT ==="
input group "=== TRADE MANAGEMENT ==="
input group "=== FILTERS ==="
input group "=== PROP FIRM RULES ==="
input group "=== VISUAL & ALERTS ==="
input group "=== EA SETTINGS ==="
```

---

## Mandatory Safety Controls

| Control | Default Value |
|---|---|
| `InpRiskPercent` | `<= 1.0` |
| `InpMaxDailyLoss` | `<= 5.0` |
| `InpMaxDrawdown` | `<= 20.0` |
| `InpMaxSpread` | symbol-appropriate, e.g. 30 for EURUSD |
| `InpMagicNumber` | unique integer |
| Stop loss | always present unless strategy has justified exit model |
| Magic + symbol filter | on every position loop |
| Margin check | `OrderCalcMargin()` before send |
| Prop firm guards | daily DD + total DD halt |

---

## MQL5 API Rules (Non-Negotiable)

- Create indicator handles in `OnInit()`, read via `CopyBuffer()`.
- Release handles in `OnDeinit()` → set to `INVALID_HANDLE` after release.
- Use `CTrade` and `trade.SetTypeFillingBySymbol(_Symbol)` or use input enum.
- Check return value of every `c_Trade.Buy()` / `c_Trade.Sell()` / `c_Trade.PositionModify()`.
- Never use MQL4-style direct indicator calls: `iMA(_Symbol, tf, 14, 0, MODE_EMA, PRICE_CLOSE, 0)`.
- Always `ArraySetAsSeries(buffer, true)` before `CopyBuffer`.
- Filter every position loop by `POSITION_SYMBOL == _Symbol && POSITION_MAGIC == magic`.
- Normalize all prices: `NormalizeDouble(price, _Digits)`.
- Pips to points for 5-digit brokers: `pips * _Point * 10`.

---

## EA File Sections (in this order)

```
1. File header comment block
2. #property directives
3. #include statements
4. Enum definitions
5. Input parameters (grouped)
6. Global variables and class instances
7. OnInit()
8. OnDeinit()
9. OnTick()
10. IsNewBar() utility
11. Signal functions (CheckBuySignal, CheckSellSignal)
12. Lot calculation (CalcLotByRisk)
13. Trade execution (OpenBuy, OpenSell)
14. Trade management (ApplyBreakEven, ApplyTrailingStop, PartialClose)
15. Filter functions (IsSpreadOK, IsInSession, IsTradeAllowed)
16. Prop firm module (CheckPropRules, CloseAllMagicPositions)
17. Dashboard update (if included)
18. Logger calls (if included)
19. Helper/utility functions
```

---

## File Header (Mandatory)

```mql5
//+------------------------------------------------------------------+
//| EA_Name.mq5                                                      |
//| Project: [Name] v[Version]                                       |
//| Author:  [Author]                                                |
//| Purpose: [One-line strategy description]                         |
//| Build:   MT5 2450+  |  Updated: [YYYY-MM-DD]                    |
//+------------------------------------------------------------------+
#property copyright "[Author]"
#property link      ""
#property version   "1.00"
#property strict
```

---

## Naming Convention Quick Reference

| Prefix | Use for | Example |
|---|---|---|
| `Inp` | Input parameters | `InpRiskPercent` |
| `g_` | Global variables | `g_LastBarTime` |
| `h_` | Indicator handles | `h_ATR`, `h_RSI` |
| `c_` | Class instances | `c_Trade`, `c_Panel` |
| none | Local variables | `lotSize`, `slDist` |
| `ALL_CAPS` | Constants | `MAX_POSITIONS` |

---

## Verification Steps (in order)

1. Compile in MetaEditor — zero errors, zero warnings.
2. Visual Strategy Tester smoke test (1 month, any recent data).
3. Backtest minimum 3 years across representative market regimes.
4. Verify: max DD within limit, spread filter works, daily loss halts trading.
5. Verify: SL/TP placed correctly, BE moves only in profit direction.
6. Verify: trailing stop moves correctly, partial close fires at right RR.
7. Forward-test on demo for minimum 3 months before any live capital.

---

## Multi-File Project Structure

For complex EAs (> 400 lines), use modular layout:

```
/Experts/ProjectName/ProjectName.mq5
/MQL5/Include/ProjectName/
    Inputs.mqh         ← all input groups
    SignalEngine.mqh   ← entry/exit signals
    TradeEngine.mqh    ← CTrade wrapper
    RiskEngine.mqh     ← lot calc + DD monitor
    FilterEngine.mqh   ← spread/session/news
    TradeManager.mqh   ← BE/trail/partial
    Dashboard.mqh      ← CDashboard class
    Logger.mqh         ← CTradeLogger class
    Utils.mqh          ← IsNewBar, IsTimeInRange, etc.
```

Label each file clearly. Every `.mqh` file must have its own header comment.
