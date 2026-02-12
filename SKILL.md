---
name: mql5-ea-expert
version: 1.1.0
language: en-US
description: Expert-level skill for creating MetaTrader 5 Expert Advisors with survival-focused approach. Covers advanced strategies (grid, martingale, ML), multi-timeframe analysis, professional money management, and backtesting optimization. Compatible with Claude, ChatGPT, Gemini, and other AI assistants.
license: MIT
last_updated: 2026-02-12
tags: [mql5, metatrader5, expert-advisor, trading, forex, risk-management, algorithmic-trading]
scope_limits: This skill teaches MQL5 EA development. It will NOT provide financial advice, guarantee profits, or recommend specific trading decisions.
---

# MQL5 Expert Advisor Development - Professional Guide

This skill enables AI assistants to generate production-ready Expert Advisors for MetaTrader 5 with a **survival-first** approach: capital preservation over maximum returns.

---

## 📚 Table of Contents

1. [AI Response Contract](#ai-response-contract)
2. [Core Philosophy](#core-philosophy)
3. [Professional EA Structure](#professional-ea-structure)
4. [Advanced Strategies](#advanced-strategies)
   - Multi-Timeframe Analysis
   - Advanced Money Management
   - Safe Grid Trading
   - Ultra-Safe Martingale
5. [Backtesting & Validation](#backtesting--validation)
6. [Pre-Deployment Checklist](#pre-deployment-checklist)
7. [Survival Tips](#survival-tips)
8. [Advanced Concepts (ML Integration)](#advanced-concepts)
9. [When to Use This Skill](#when-to-use-this-skill)

---

## AI Response Contract

When generating MQL5 Expert Advisors, you MUST:

### Output Requirements
1. **Restate requirements** - Confirm user's strategy and parameters
2. **List all inputs** - Organized by category (Trading, Risk, Filters, Advanced)
3. **Output single .mq5 file** - Complete, compile-ready code
4. **Include test steps** - How to verify the EA works
5. **Add risk warnings** - Especially for grid/martingale/high-risk strategies

### Safety Rules
1. **NEVER remove risk management** - Even if user requests it, always include:
   - Max risk per trade (default 1%)
   - Daily loss limits (default 5%)
   - Max drawdown protection (default 20%)
   - Spread filters
   - Magic number for position tracking

2. **REFUSE dangerous configurations:**
   - Martingale multiplier > 2.0 → Force cap at 1.5
   - Martingale steps > 5 → Force cap at 3-4
   - Risk per trade > 5% → Warn and suggest 1%
   - No stop loss → Refuse unless valid strategy reason

3. **Warning triggers** - Add explicit warnings when:
   - Grid/Martingale strategies requested
   - High leverage implied
   - Unrealistic profit targets mentioned
   - Insufficient risk management

### Code Quality Standards
1. **Compile-ready** - Code must compile without errors in MetaEditor
2. **Error handling** - Check all CopyBuffer, trade operations
3. **MQL5 API correctness:**
   - Use indicator handles + CopyBuffer (NOT direct iMA() calls)
   - Use `trade.PositionModify(symbol, sl, tp)` NOT by ticket
   - Use `trade.SetTypeFillingBySymbol(_Symbol)` for filling mode
   - Filter positions by Symbol AND MagicNumber
4. **Comments** - Explain non-obvious logic
5. **Consistent style** - Follow MQL5 coding standards

### Questions to Ask
Before generating code, ask when unclear:
- **Strategy edge**: "What's the logical edge for this strategy?"
- **Risk tolerance**: "What's your maximum acceptable drawdown?"
- **Timeframe**: "Which timeframe will you trade?"
- **Testing period**: "How long will you demo-test before live?"

---

## CORE PHILOSOPHY

Before writing code, understand these principles:

1. **Capital Preservation is King** - Protect capital as the highest priority
2. **Risk-Adjusted Returns** - 50% profit with 10% drawdown > 200% profit with 60% drawdown
3. **Market Adaptability** - Markets change; EAs must adapt
4. **Edge Validation** - Every strategy must have a measurable, logical edge
5. **Psychological Robustness** - EAs must be executable without panic during drawdowns

---

## PROFESSIONAL EA STRUCTURE

### Base Template with Best Practices

```mql5
//+------------------------------------------------------------------+
//|                                                    Expert_EA.mq5 |
//|                                      [Your Name or Company Name] |
//+------------------------------------------------------------------+
#property copyright   "[Your Name]"
#property link        "[Your Website]"
#property version     "1.00"
#property description "Description of EA strategy and logic"

// Include libraries
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\AccountInfo.mqh>

// Input parameters - organized by category
//--- Trading Parameters
input group "=== Trading Settings ==="
input ENUM_TIMEFRAMES Timeframe = PERIOD_H1;           // Main Timeframe
input double          LotSize = 0.01;                  // Fixed Lot Size
input bool            UseAutoLot = true;                // Use Auto Lot Sizing
input double          RiskPercent = 1.0;               // Risk Per Trade (%)
input int             MagicNumber = 123456;            // Magic Number

//--- Strategy Parameters
input group "=== Strategy Settings ==="
input int             FastMA = 10;                      // Fast MA Period
input int             SlowMA = 30;                      // Slow MA Period
input ENUM_MA_METHOD  MAMethod = MODE_EMA;             // MA Method
input ENUM_APPLIED_PRICE MAPrice = PRICE_CLOSE;        // MA Applied Price

//--- Risk Management
input group "=== Risk Management ==="
input double          MaxDailyLoss = 5.0;              // Max Daily Loss (%)
input double          MaxDailyProfit = 10.0;           // Daily Profit Target (%)
input int             MaxSpreadPoints = 30;            // Max Spread (points)
input double          MaxDrawdownPercent = 20.0;       // Max Drawdown (%)

//--- Time Filter
input group "=== Time Filter ==="
input bool            UseTimeFilter = true;             // Use Time Filter
input int             StartHour = 0;                    // Start Hour (Server Time)
input int             EndHour = 23;                     // End Hour (Server Time)
input bool            TradeMonday = true;               // Trade on Monday
input bool            TradeTuesday = true;              // Trade on Tuesday
input bool            TradeWednesday = true;            // Trade on Wednesday
input bool            TradeThursday = true;             // Trade on Thursday
input bool            TradeFriday = true;               // Trade on Friday

//--- Advanced Settings
input group "=== Advanced Settings ==="
input int             Slippage = 10;                    // Max Slippage (points)
input bool            UseBreakEven = true;              // Use Break Even
input double          BreakEvenPoints = 20;            // Break Even Points
input double          BreakEvenProfit = 10;            // BE Lock Profit Points
input bool            UseTrailingStop = true;           // Use Trailing Stop
input double          TrailingStart = 30;              // Trailing Start (points)
input double          TrailingStop = 20;               // Trailing Stop (points)
input double          TrailingStep = 10;               // Trailing Step (points)

// Global variables
CTrade            trade;
CPositionInfo     position;
COrderInfo        order;
CAccountInfo      account;

int               handleFastMA;
int               handleSlowMA;
double            fastMABuffer[];
double            slowMABuffer[];

datetime          lastBarTime = 0;
double            dailyStartBalance = 0;
datetime          dailyStartTime = 0;
bool              dailyTargetReached = false;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   // Set trade parameters
   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetDeviationInPoints(Slippage);
   trade.SetTypeFillingBySymbol(_Symbol); // Auto-detect supported filling mode
   trade.SetAsyncMode(false);
   
   // Initialize indicators
   handleFastMA = iMA(_Symbol, Timeframe, FastMA, 0, MAMethod, MAPrice);
   handleSlowMA = iMA(_Symbol, Timeframe, SlowMA, 0, MAMethod, MAPrice);
   
   if(handleFastMA == INVALID_HANDLE || handleSlowMA == INVALID_HANDLE)
   {
      Print("Error creating indicators");
      return INIT_FAILED;
   }
   
   // Set array as series
   ArraySetAsSeries(fastMABuffer, true);
   ArraySetAsSeries(slowMABuffer, true);
   
   // Initialize daily tracking
   dailyStartBalance = account.Balance();
   dailyStartTime = TimeCurrent();
   
   Print("EA Initialized Successfully");
   Print("Account Balance: ", account.Balance());
   Print("Account Leverage: ", account.Leverage());
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Release indicator handles
   if(handleFastMA != INVALID_HANDLE) IndicatorRelease(handleFastMA);
   if(handleSlowMA != INVALID_HANDLE) IndicatorRelease(handleSlowMA);
   
   Print("EA Deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check if new bar
   if(!IsNewBar()) return;
   
   // Update daily tracking
   UpdateDailyTracking();
   
   // Check daily limits
   if(IsDailyLimitReached()) return;
   
   // Update indicator buffers
   if(!UpdateIndicators()) return;
   
   // Check trading conditions
   if(!IsTradingAllowed()) return;
   
   // Manage existing positions
   ManagePositions();
   
   // Check for new trade signals
   CheckTradeSignals();
}

//+------------------------------------------------------------------+
//| Check if new bar has formed                                        |
//+------------------------------------------------------------------+
bool IsNewBar()
{
   datetime currentBarTime = iTime(_Symbol, Timeframe, 0);
   if(currentBarTime != lastBarTime)
   {
      lastBarTime = currentBarTime;
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| Update daily tracking                                              |
//+------------------------------------------------------------------+
void UpdateDailyTracking()
{
   datetime currentTime = TimeCurrent();
   MqlDateTime dt;
   TimeToStruct(currentTime, dt);
   
   MqlDateTime dtStart;
   TimeToStruct(dailyStartTime, dtStart);
   
   // Reset daily tracking if new day
   if(dt.day != dtStart.day || dt.mon != dtStart.mon || dt.year != dtStart.year)
   {
      dailyStartBalance = account.Balance();
      dailyStartTime = currentTime;
      dailyTargetReached = false;
      Print("New trading day started. Balance: ", dailyStartBalance);
   }
}

//+------------------------------------------------------------------+
//| Check if daily limits reached                                      |
//+------------------------------------------------------------------+
bool IsDailyLimitReached()
{
   if(dailyTargetReached) return true;
   
   double currentBalance = account.Balance();
   double dailyProfitLoss = ((currentBalance - dailyStartBalance) / dailyStartBalance) * 100;
   
   // Check daily loss limit
   if(dailyProfitLoss <= -MaxDailyLoss)
   {
      dailyTargetReached = true;
      Print("Daily loss limit reached: ", dailyProfitLoss, "%");
      CloseAllPositions();
      return true;
   }
   
   // Check daily profit target
   if(dailyProfitLoss >= MaxDailyProfit)
   {
      dailyTargetReached = true;
      Print("Daily profit target reached: ", dailyProfitLoss, "%");
      CloseAllPositions();
      return true;
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Update indicator buffers                                           |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
   if(CopyBuffer(handleFastMA, 0, 0, 3, fastMABuffer) < 3) return false;
   if(CopyBuffer(handleSlowMA, 0, 0, 3, slowMABuffer) < 3) return false;
   return true;
}

//+------------------------------------------------------------------+
//| Check if trading is allowed                                        |
//+------------------------------------------------------------------+
bool IsTradingAllowed()
{
   // Check if trading is allowed on account
   if(!account.TradeAllowed())
   {
      Print("Trading is not allowed on this account");
      return false;
   }
   
   // Check terminal connection
   if(!TerminalInfoInteger(TERMINAL_CONNECTED))
   {
      Print("No connection to trade server");
      return false;
   }
   
   // Check spread
   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > MaxSpreadPoints)
   {
      Print("Spread too high: ", spread, " points");
      return false;
   }
   
   // Check time filter
   if(UseTimeFilter && !IsTimeToTrade())
   {
      return false;
   }
   
   // Check drawdown limit
   if(!CheckDrawdownLimit())
   {
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Check time filter                                                  |
//+------------------------------------------------------------------+
bool IsTimeToTrade()
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   
   // Check day of week
   switch(dt.day_of_week)
   {
      case 1: if(!TradeMonday) return false; break;
      case 2: if(!TradeTuesday) return false; break;
      case 3: if(!TradeWednesday) return false; break;
      case 4: if(!TradeThursday) return false; break;
      case 5: if(!TradeFriday) return false; break;
      default: return false; // Weekend
   }
   
   // Check hour range
   if(dt.hour < StartHour || dt.hour >= EndHour)
   {
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Check drawdown limit                                               |
//+------------------------------------------------------------------+
bool CheckDrawdownLimit()
{
   double balance = account.Balance();
   double equity = account.Equity();
   
   if(balance > 0)
   {
      double currentDrawdown = ((balance - equity) / balance) * 100;
      if(currentDrawdown > MaxDrawdownPercent)
      {
         Print("Max drawdown reached: ", currentDrawdown, "%");
         CloseAllPositions();
         return false;
      }
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk                                   |
//+------------------------------------------------------------------+
double CalculateLotSize(double stopLossPoints)
{
   if(!UseAutoLot) return LotSize;
   
   double balance = account.Balance();
   double riskAmount = balance * (RiskPercent / 100.0);
   
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   double lotSize = 0;
   if(stopLossPoints > 0)
   {
      double moneyPerPoint = (tickValue / tickSize) * point;
      lotSize = riskAmount / (stopLossPoints * moneyPerPoint);
   }
   else
   {
      lotSize = LotSize;
   }
   
   // Normalize lot size
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   lotSize = MathFloor(lotSize / lotStep) * lotStep;
   lotSize = MathMax(lotSize, minLot);
   lotSize = MathMin(lotSize, maxLot);
   
   return lotSize;
}

//+------------------------------------------------------------------+
//| Manage existing positions                                          |
//+------------------------------------------------------------------+
void ManagePositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(position.SelectByIndex(i))
      {
         if(position.Symbol() == _Symbol && position.Magic() == MagicNumber)
         {
            // Break even management
            if(UseBreakEven)
            {
               MoveToBreakEven(position.Ticket());
            }
            
            // Trailing stop management
            if(UseTrailingStop)
            {
               TrailStop(position.Ticket());
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Move stop loss to break even                                       |
//+------------------------------------------------------------------+
void MoveToBreakEven(ulong ticket)
{
   if(!position.SelectByTicket(ticket)) return;
   
   double openPrice = position.PriceOpen();
   double currentSL = position.StopLoss();
   double currentPrice = (position.Type() == POSITION_TYPE_BUY) ? 
                         SymbolInfoDouble(_Symbol, SYMBOL_BID) : 
                         SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double breakEvenPrice = 0;
   
   if(position.Type() == POSITION_TYPE_BUY)
   {
      double profitPoints = (currentPrice - openPrice) / point;
      if(profitPoints >= BreakEvenPoints && (currentSL < openPrice || currentSL == 0))
      {
         breakEvenPrice = openPrice + (BreakEvenProfit * point);
         if(trade.PositionModify(_Symbol, breakEvenPrice, position.TakeProfit()))
         {
            Print("Break even set for BUY position: ", ticket);
         }
      }
   }
   else // SELL
   {
      double profitPoints = (openPrice - currentPrice) / point;
      if(profitPoints >= BreakEvenPoints && (currentSL > openPrice || currentSL == 0))
      {
         breakEvenPrice = openPrice - (BreakEvenProfit * point);
         if(trade.PositionModify(_Symbol, breakEvenPrice, position.TakeProfit()))
         {
            Print("Break even set for SELL position: ", ticket);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Trailing stop management                                           |
//+------------------------------------------------------------------+
void TrailStop(ulong ticket)
{
   if(!position.SelectByTicket(ticket)) return;
   
   double openPrice = position.PriceOpen();
   double currentSL = position.StopLoss();
   double currentPrice = (position.Type() == POSITION_TYPE_BUY) ? 
                         SymbolInfoDouble(_Symbol, SYMBOL_BID) : 
                         SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double newSL = 0;
   
   if(position.Type() == POSITION_TYPE_BUY)
   {
      double profitPoints = (currentPrice - openPrice) / point;
      if(profitPoints >= TrailingStart)
      {
         newSL = currentPrice - (TrailingStop * point);
         
         // Only move SL up
         if(newSL > currentSL + (TrailingStep * point) || currentSL == 0)
         {
            if(trade.PositionModify(_Symbol, newSL, position.TakeProfit()))
            {
               Print("Trailing stop updated for BUY: ", ticket, " New SL: ", newSL);
            }
         }
      }
   }
   else // SELL
   {
      double profitPoints = (openPrice - currentPrice) / point;
      if(profitPoints >= TrailingStart)
      {
         newSL = currentPrice + (TrailingStop * point);
         
         // Only move SL down
         if(newSL < currentSL - (TrailingStep * point) || currentSL == 0)
         {
            if(trade.PositionModify(_Symbol, newSL, position.TakeProfit()))
            {
               Print("Trailing stop updated for SELL: ", ticket, " New SL: ", newSL);
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Check for trade signals                                            |
//+------------------------------------------------------------------+
void CheckTradeSignals()
{
   // Check if already have position for this EA
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(position.SelectByIndex(i))
      {
         if(position.Symbol() == _Symbol && position.Magic() == MagicNumber)
            return; // Already have position
      }
   }
   
   // Get current MA values
   double fastMA0 = fastMABuffer[0];
   double fastMA1 = fastMABuffer[1];
   double slowMA0 = slowMABuffer[0];
   double slowMA1 = slowMABuffer[1];
   
   // BUY Signal: Fast MA crosses above Slow MA
   if(fastMA1 <= slowMA1 && fastMA0 > slowMA0)
   {
      OpenBuyTrade();
   }
   
   // SELL Signal: Fast MA crosses below Slow MA
   if(fastMA1 >= slowMA1 && fastMA0 < slowMA0)
   {
      OpenSellTrade();
   }
}

//+------------------------------------------------------------------+
//| Open buy trade                                                     |
//+------------------------------------------------------------------+
void OpenBuyTrade()
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   // Calculate SL and TP
   double sl = ask - (100 * point); // 100 points SL
   double tp = ask + (200 * point); // 200 points TP (2:1 RR)
   
   // Calculate lot size
   double lotSize = CalculateLotSize(100);
   
   // Open trade
   if(trade.Buy(lotSize, _Symbol, ask, sl, tp, "Buy Signal"))
   {
      Print("BUY order opened: Lot=", lotSize, " SL=", sl, " TP=", tp);
   }
   else
   {
      Print("Error opening BUY order: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Open sell trade                                                    |
//+------------------------------------------------------------------+
void OpenSellTrade()
{
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   // Calculate SL and TP
   double sl = bid + (100 * point); // 100 points SL
   double tp = bid - (200 * point); // 200 points TP (2:1 RR)
   
   // Calculate lot size
   double lotSize = CalculateLotSize(100);
   
   // Open trade
   if(trade.Sell(lotSize, _Symbol, bid, sl, tp, "Sell Signal"))
   {
      Print("SELL order opened: Lot=", lotSize, " SL=", sl, " TP=", tp);
   }
   else
   {
      Print("Error opening SELL order: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Close all positions                                                |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(position.SelectByIndex(i))
      {
         if(position.Symbol() == _Symbol && position.Magic() == MagicNumber)
         {
            trade.PositionClose(position.Symbol());
            Print("Position closed: ", position.Ticket());
         }
      }
   }
}
//+------------------------------------------------------------------+
```

---

## ADVANCED STRATEGIES IMPLEMENTATION

### 1. MULTI-TIMEFRAME ANALYSIS (MTF)

Multi-timeframe analysis memberikan konfirmasi dari berbagai perspektif waktu. Trend di timeframe besar + entry di timeframe kecil = edge yang kuat.

```mql5
//+------------------------------------------------------------------+
//| Multi-Timeframe Analysis Class                                     |
//+------------------------------------------------------------------+
class CMultiTimeframeAnalysis
{
private:
   string            m_symbol;
   ENUM_TIMEFRAMES   m_tf1;  // Higher timeframe (trend)
   ENUM_TIMEFRAMES   m_tf2;  // Medium timeframe (filter)
   ENUM_TIMEFRAMES   m_tf3;  // Lower timeframe (entry)
   
   int               m_handleMA_TF1;
   int               m_handleMA_TF2;
   int               m_handleMA_TF3;
   
   double            m_bufferMA_TF1[];
   double            m_bufferMA_TF2[];
   double            m_bufferMA_TF3[];

public:
   CMultiTimeframeAnalysis(string symbol, ENUM_TIMEFRAMES tf1, ENUM_TIMEFRAMES tf2, ENUM_TIMEFRAMES tf3)
   {
      m_symbol = symbol;
      m_tf1 = tf1;
      m_tf2 = tf2;
      m_tf3 = tf3;
      
      // Initialize indicators for each timeframe
      m_handleMA_TF1 = iMA(m_symbol, m_tf1, 50, 0, MODE_EMA, PRICE_CLOSE);
      m_handleMA_TF2 = iMA(m_symbol, m_tf2, 50, 0, MODE_EMA, PRICE_CLOSE);
      m_handleMA_TF3 = iMA(m_symbol, m_tf3, 20, 0, MODE_EMA, PRICE_CLOSE);
      
      ArraySetAsSeries(m_bufferMA_TF1, true);
      ArraySetAsSeries(m_bufferMA_TF2, true);
      ArraySetAsSeries(m_bufferMA_TF3, true);
   }
   
   ~CMultiTimeframeAnalysis()
   {
      if(m_handleMA_TF1 != INVALID_HANDLE) IndicatorRelease(m_handleMA_TF1);
      if(m_handleMA_TF2 != INVALID_HANDLE) IndicatorRelease(m_handleMA_TF2);
      if(m_handleMA_TF3 != INVALID_HANDLE) IndicatorRelease(m_handleMA_TF3);
   }
   
   //+------------------------------------------------------------------+
   //| Get trend direction from higher timeframe                         |
   //+------------------------------------------------------------------+
   int GetTrendDirection()
   {
      CopyBuffer(m_handleMA_TF1, 0, 0, 3, m_bufferMA_TF1);
      
      double close0 = iClose(m_symbol, m_tf1, 0);
      double close1 = iClose(m_symbol, m_tf1, 1);
      double ma0 = m_bufferMA_TF1[0];
      double ma1 = m_bufferMA_TF1[1];
      
      // Strong uptrend
      if(close0 > ma0 && close1 > ma1 && ma0 > ma1)
         return 1;
      
      // Strong downtrend
      if(close0 < ma0 && close1 < ma1 && ma0 < ma1)
         return -1;
      
      // No clear trend
      return 0;
   }
   
   //+------------------------------------------------------------------+
   //| Check if all timeframes align for buy                             |
   //+------------------------------------------------------------------+
   bool IsBuySignal()
   {
      // Update all buffers
      CopyBuffer(m_handleMA_TF1, 0, 0, 2, m_bufferMA_TF1);
      CopyBuffer(m_handleMA_TF2, 0, 0, 2, m_bufferMA_TF2);
      CopyBuffer(m_handleMA_TF3, 0, 0, 3, m_bufferMA_TF3);
      
      // TF1: Higher timeframe trend must be up
      double close_tf1 = iClose(m_symbol, m_tf1, 0);
      if(close_tf1 <= m_bufferMA_TF1[0]) return false;
      
      // TF2: Medium timeframe must confirm
      double close_tf2 = iClose(m_symbol, m_tf2, 0);
      if(close_tf2 <= m_bufferMA_TF2[0]) return false;
      
      // TF3: Entry timeframe - look for crossover
      double close_tf3_0 = iClose(m_symbol, m_tf3, 0);
      double close_tf3_1 = iClose(m_symbol, m_tf3, 1);
      
      // Bullish crossover on entry timeframe
      if(close_tf3_1 <= m_bufferMA_TF3[1] && close_tf3_0 > m_bufferMA_TF3[0])
         return true;
      
      return false;
   }
   
   //+------------------------------------------------------------------+
   //| Check if all timeframes align for sell                            |
   //+------------------------------------------------------------------+
   bool IsSellSignal()
   {
      // Update all buffers
      CopyBuffer(m_handleMA_TF1, 0, 0, 2, m_bufferMA_TF1);
      CopyBuffer(m_handleMA_TF2, 0, 0, 2, m_bufferMA_TF2);
      CopyBuffer(m_handleMA_TF3, 0, 0, 3, m_bufferMA_TF3);
      
      // TF1: Higher timeframe trend must be down
      double close_tf1 = iClose(m_symbol, m_tf1, 0);
      if(close_tf1 >= m_bufferMA_TF1[0]) return false;
      
      // TF2: Medium timeframe must confirm
      double close_tf2 = iClose(m_symbol, m_tf2, 0);
      if(close_tf2 >= m_bufferMA_TF2[0]) return false;
      
      // TF3: Entry timeframe - look for crossover
      double close_tf3_0 = iClose(m_symbol, m_tf3, 0);
      double close_tf3_1 = iClose(m_symbol, m_tf3, 1);
      
      // Bearish crossover on entry timeframe
      if(close_tf3_1 >= m_bufferMA_TF3[1] && close_tf3_0 < m_bufferMA_TF3[0])
         return true;
      
      return false;
   }
   
   //+------------------------------------------------------------------+
   //| Get strength of alignment (0-100)                                 |
   //+------------------------------------------------------------------+
   double GetAlignmentStrength()
   {
      CopyBuffer(m_handleMA_TF1, 0, 0, 1, m_bufferMA_TF1);
      CopyBuffer(m_handleMA_TF2, 0, 0, 1, m_bufferMA_TF2);
      CopyBuffer(m_handleMA_TF3, 0, 0, 1, m_bufferMA_TF3);
      
      double close_tf1 = iClose(m_symbol, m_tf1, 0);
      double close_tf2 = iClose(m_symbol, m_tf2, 0);
      double close_tf3 = iClose(m_symbol, m_tf3, 0);
      
      double dist1 = MathAbs(close_tf1 - m_bufferMA_TF1[0]) / m_bufferMA_TF1[0] * 100;
      double dist2 = MathAbs(close_tf2 - m_bufferMA_TF2[0]) / m_bufferMA_TF2[0] * 100;
      double dist3 = MathAbs(close_tf3 - m_bufferMA_TF3[0]) / m_bufferMA_TF3[0] * 100;
      
      // Average distance from MA across timeframes
      double avgDistance = (dist1 + dist2 + dist3) / 3.0;
      
      // Convert to strength (closer = stronger)
      double strength = 100 - MathMin(avgDistance * 10, 100);
      
      return strength;
   }
};
```

**How to Use MTF in Your EA:**
```mql5
// Global variables
CMultiTimeframeAnalysis *mtf;

// In OnInit()
int OnInit()
{
   mtf = new CMultiTimeframeAnalysis(_Symbol, PERIOD_H4, PERIOD_H1, PERIOD_M15);
   return INIT_SUCCEEDED;
}

// In OnDeinit()
void OnDeinit(const int reason)
{
   if(mtf != NULL)
   {
      delete mtf;
      mtf = NULL;
   }
}

// In OnTick() or CheckTradeSignals()
void CheckTradeSignals()
{
   if(mtf->IsBuySignal())
   {
      double strength = mtf->GetAlignmentStrength();
      if(strength > 70) // Only trade if alignment is strong
      {
         OpenBuyTrade();
      }
   }
   
   if(mtf->IsSellSignal())
   {
      double strength = mtf->GetAlignmentStrength();
      if(strength > 70)
      {
         OpenSellTrade();
      }
   }
}
```

---

### 2. ADVANCED MONEY MANAGEMENT

Money management yang proper adalah kunci survival. Ini bukan tentang profit maksimal, tapi tentang TIDAK BANGKRUT.

```mql5
//+------------------------------------------------------------------+
//| Advanced Money Management Class                                    |
//+------------------------------------------------------------------+
class CMoneyManagement
{
private:
   double            m_initialBalance;
   double            m_maxRiskPerTrade;        // % of balance
   double            m_maxDailyRisk;           // % of balance
   double            m_maxDrawdown;            // % of balance
   double            m_dailyRiskUsed;
   
   double            m_kellyFraction;          // Kelly Criterion multiplier
   bool              m_useKelly;
   
   int               m_consecutiveLosses;
   int               m_consecutiveWins;
   double            m_winRate;
   double            m_avgWin;
   double            m_avgLoss;

public:
   CMoneyManagement(double initialBalance, double riskPerTrade, double dailyRisk, double maxDD)
   {
      m_initialBalance = initialBalance;
      m_maxRiskPerTrade = riskPerTrade;
      m_maxDailyRisk = dailyRisk;
      m_maxDrawdown = maxDD;
      m_dailyRiskUsed = 0;
      
      m_kellyFraction = 0.25; // Conservative Kelly (1/4 of full Kelly)
      m_useKelly = false;
      
      m_consecutiveLosses = 0;
      m_consecutiveWins = 0;
      m_winRate = 0.5; // Start with 50% assumption
      m_avgWin = 0;
      m_avgLoss = 0;
   }
   
   //+------------------------------------------------------------------+
   //| Calculate position size based on fixed risk                       |
   //+------------------------------------------------------------------+
   double CalculatePositionSize(string symbol, double stopLossPoints)
   {
      CAccountInfo account;
      double balance = account.Balance();
      
      // Check if we've exceeded daily risk limit
      if(m_dailyRiskUsed >= m_maxDailyRisk)
      {
         Print("Daily risk limit reached: ", m_dailyRiskUsed, "%");
         return 0;
      }
      
      // Calculate risk amount
      double riskPercent = GetAdjustedRiskPercent();
      double riskAmount = balance * (riskPercent / 100.0);
      
      // Calculate lot size
      double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      
      if(stopLossPoints <= 0) return 0;
      
      double moneyPerPoint = (tickValue / tickSize) * point;
      double lotSize = riskAmount / (stopLossPoints * moneyPerPoint);
      
      // Normalize lot size
      lotSize = NormalizeLotSize(symbol, lotSize);
      
      // Update daily risk used
      m_dailyRiskUsed += riskPercent;
      
      return lotSize;
   }
   
   //+------------------------------------------------------------------+
   //| Get adjusted risk percent based on performance                    |
   //+------------------------------------------------------------------+
   double GetAdjustedRiskPercent()
   {
      double baseRisk = m_maxRiskPerTrade;
      
      // Reduce risk after consecutive losses (check highest threshold first)
      if(m_consecutiveLosses >= 5)
      {
         baseRisk *= 0.25; // Cut to 1/4
         Print("Risk severely reduced: ", m_consecutiveLosses, " losses");
      }
      else if(m_consecutiveLosses >= 3)
      {
         baseRisk *= 0.5; // Cut risk in half
         Print("Risk reduced due to consecutive losses: ", m_consecutiveLosses);
      }
      
      // Increase risk slightly after consecutive wins (but cap it)
      if(m_consecutiveWins >= 3)
      {
         baseRisk *= 1.2; // Increase 20%
         baseRisk = MathMin(baseRisk, m_maxRiskPerTrade * 1.5); // Max 1.5x
      }
      
      // Use Kelly Criterion if enabled and we have enough data
      if(m_useKelly && m_avgWin > 0 && m_avgLoss > 0)
      {
         double kellyRisk = CalculateKellyRisk();
         baseRisk = MathMin(baseRisk, kellyRisk);
      }
      
      return baseRisk;
   }
   
   //+------------------------------------------------------------------+
   //| Calculate Kelly Criterion risk                                    |
   //+------------------------------------------------------------------+
   double CalculateKellyRisk()
   {
      // Kelly % = W - [(1-W) / R]
      // W = Win rate
      // R = Win/Loss ratio
      
      if(m_avgLoss == 0) return m_maxRiskPerTrade;
      
      double winLossRatio = m_avgWin / m_avgLoss;
      double kellyPercent = m_winRate - ((1 - m_winRate) / winLossRatio);
      
      // Apply Kelly fraction for safety (never use full Kelly!)
      kellyPercent *= m_kellyFraction;
      
      // Cap at max risk per trade
      kellyPercent = MathMax(kellyPercent, 0.1); // Minimum 0.1%
      kellyPercent = MathMin(kellyPercent, m_maxRiskPerTrade);
      
      return kellyPercent;
   }
   
   //+------------------------------------------------------------------+
   //| Normalize lot size according to broker requirements               |
   //+------------------------------------------------------------------+
   double NormalizeLotSize(string symbol, double lotSize)
   {
      double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
      
      lotSize = MathFloor(lotSize / lotStep) * lotStep;
      lotSize = MathMax(lotSize, minLot);
      lotSize = MathMin(lotSize, maxLot);
      
      return lotSize;
   }
   
   //+------------------------------------------------------------------+
   //| Update statistics after trade close                               |
   //+------------------------------------------------------------------+
   void UpdateStats(double profit)
   {
      if(profit > 0)
      {
         m_consecutiveWins++;
         m_consecutiveLosses = 0;
         
         // Update avg win
         if(m_avgWin == 0)
            m_avgWin = profit;
         else
            m_avgWin = (m_avgWin * 0.8) + (profit * 0.2); // EMA
      }
      else if(profit < 0)
      {
         m_consecutiveLosses++;
         m_consecutiveWins = 0;
         
         // Update avg loss
         if(m_avgLoss == 0)
            m_avgLoss = MathAbs(profit);
         else
            m_avgLoss = (m_avgLoss * 0.8) + (MathAbs(profit) * 0.2); // EMA
      }
      
      // Update win rate (simple moving average)
      // You should track this more accurately with total trades
      if(profit > 0)
         m_winRate = (m_winRate * 0.9) + (1.0 * 0.1);
      else if(profit < 0)
         m_winRate = (m_winRate * 0.9) + (0.0 * 0.1);
   }
   
   //+------------------------------------------------------------------+
   //| Reset daily risk counter                                          |
   //+------------------------------------------------------------------+
   void ResetDailyRisk()
   {
      m_dailyRiskUsed = 0;
   }
   
   //+------------------------------------------------------------------+
   //| Check if we can take new trade                                    |
   //+------------------------------------------------------------------+
   bool CanTakeNewTrade()
   {
      CAccountInfo account;
      
      // Check daily risk limit
      if(m_dailyRiskUsed >= m_maxDailyRisk)
         return false;
      
      // Check drawdown limit
      double balance = account.Balance();
      double equity = account.Equity();
      double currentDD = ((balance - equity) / balance) * 100;
      
      if(currentDD >= m_maxDrawdown)
      {
         Print("Max drawdown reached: ", currentDD, "%");
         return false;
      }
      
      // Stop trading after 5 consecutive losses
      if(m_consecutiveLosses >= 5)
      {
         Print("Too many consecutive losses. Pausing trading.");
         return false;
      }
      
      return true;
   }
   
   //+------------------------------------------------------------------+
   //| Enable Kelly Criterion (use with caution!)                        |
   //+------------------------------------------------------------------+
   void EnableKelly(bool enable, double fraction = 0.25)
   {
      m_useKelly = enable;
      m_kellyFraction = fraction;
   }
   
   //+------------------------------------------------------------------+
   //| Get current statistics                                             |
   //+------------------------------------------------------------------+
   string GetStats()
   {
      string stats = StringFormat(
         "MM Stats: Wins=%d, Losses=%d, WinRate=%.2f%%, AvgWin=%.2f, AvgLoss=%.2f, DailyRisk=%.2f%%",
         m_consecutiveWins, m_consecutiveLosses, m_winRate * 100,
         m_avgWin, m_avgLoss, m_dailyRiskUsed
      );
      return stats;
   }
};
```

**How to Use Money Management:**
```mql5
// Global variables
CMoneyManagement *mm;

// In OnInit()
int OnInit()
{
   mm = new CMoneyManagement(
      account.Balance(),    // Initial balance
      1.0,                  // Max risk per trade: 1%
      5.0,                  // Max daily risk: 5%
      20.0                  // Max drawdown: 20%
   );
   
   // Optional: Enable Kelly Criterion
   mm->EnableKelly(true, 0.25); // Use 1/4 Kelly
   
   return INIT_SUCCEEDED;
}

// In OnDeinit()
void OnDeinit(const int reason)
{
   if(mm != NULL)
   {
      delete mm;
      mm = NULL;
   }
}

// Before opening trade
void CheckTradeSignals()
{
   if(mm->CanTakeNewTrade())
   {
      double stopLossPoints = 50; // Your SL in points
      double lotSize = mm->CalculatePositionSize(_Symbol, stopLossPoints);
      
      if(lotSize > 0)
      {
         // Open trade with calculated lot size
      }
   }
}

// After trade closes (in OnTradeTransaction or check history)
double profit = CalculateTradeProfit(ticket); // Your function
mm->UpdateStats(profit);

// Reset daily at start of new day
if(IsNewDay())
{
   mm->ResetDailyRisk();
}
```

---

### 3. GRID TRADING SYSTEM (SAFE VERSION)

Grid trading can be profitable but is also VERY DANGEROUS without protection. This is a safer grid implementation.

```mql5
//+------------------------------------------------------------------+
//| Safe Grid Trading System                                           |
//+------------------------------------------------------------------+
class CSafeGridSystem
{
private:
   string            m_symbol;
   int               m_magicNumber;
   
   double            m_gridSize;              // Distance between grid levels (points)
   int               m_maxGridLevels;         // Maximum number of grid levels
   double            m_lotMultiplier;         // Lot multiplier for each level (1.0 = no multiplier)
   double            m_baseLot;               // Starting lot size
   
   double            m_maxDrawdownPercent;    // Max allowed drawdown before stopping
   double            m_profitTarget;          // Close all at this profit
   
   bool              m_isActive;
   double            m_firstOrderPrice;
   int               m_currentLevel;
   double            m_totalVolume;
   
   CTrade            trade;
   CPositionInfo     position;

public:
   CSafeGridSystem(string symbol, int magic, double gridSize, int maxLevels, double baseLot)
   {
      m_symbol = symbol;
      m_magicNumber = magic;
      m_gridSize = gridSize;
      m_maxGridLevels = maxLevels;
      m_baseLot = baseLot;
      m_lotMultiplier = 1.0; // Default: no multiplier (safer)
      
      m_maxDrawdownPercent = 15.0; // Stop if drawdown > 15%
      m_profitTarget = 100.0; // Close all at $100 profit
      
      m_isActive = false;
      m_firstOrderPrice = 0;
      m_currentLevel = 0;
      m_totalVolume = 0;
      
      trade.SetExpertMagicNumber(magic);
   }
   
   //+------------------------------------------------------------------+
   //| Initialize grid from first order                                  |
   //+------------------------------------------------------------------+
   void InitializeGrid(bool isBuy, double price)
   {
      m_isActive = true;
      m_firstOrderPrice = price;
      m_currentLevel = 1;
      m_totalVolume = m_baseLot;
      
      Print("Grid initialized at ", price, " Direction: ", (isBuy ? "BUY" : "SELL"));
   }
   
   //+------------------------------------------------------------------+
   //| Check if should add grid level                                    |
   //+------------------------------------------------------------------+
   bool ShouldAddGridLevel()
   {
      if(!m_isActive) return false;
      if(m_currentLevel >= m_maxGridLevels) return false;
      
      // Check drawdown limit
      if(!CheckDrawdownLimit()) return false;
      
      // Get first position direction
      bool isFirstBuy = GetFirstPositionType();
      double currentPrice = isFirstBuy ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) : 
                                         SymbolInfoDouble(m_symbol, SYMBOL_BID);
      double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
      
      // Calculate distance from first order
      double distance = 0;
      if(isFirstBuy)
         distance = (m_firstOrderPrice - currentPrice) / point;
      else
         distance = (currentPrice - m_firstOrderPrice) / point;
      
      // Check if price has moved enough for next grid level
      int requiredDistance = (int)(m_gridSize * m_currentLevel);
      if(distance >= requiredDistance)
      {
         return true;
      }
      
      return false;
   }
   
   //+------------------------------------------------------------------+
   //| Add new grid level                                                |
   //+------------------------------------------------------------------+
   void AddGridLevel()
   {
      bool isFirstBuy = GetFirstPositionType();
      double currentPrice = isFirstBuy ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) : 
                                         SymbolInfoDouble(m_symbol, SYMBOL_BID);
      
      // Calculate lot size for this level
      double lotSize = m_baseLot * MathPow(m_lotMultiplier, m_currentLevel);
      lotSize = NormalizeLotSize(lotSize);
      
      // Open order
      bool success = false;
      if(isFirstBuy)
         success = trade.Buy(lotSize, m_symbol, currentPrice, 0, 0, "Grid Level " + IntegerToString(m_currentLevel + 1));
      else
         success = trade.Sell(lotSize, m_symbol, currentPrice, 0, 0, "Grid Level " + IntegerToString(m_currentLevel + 1));
      
      if(success)
      {
         m_currentLevel++;
         m_totalVolume += lotSize;
         Print("Grid level ", m_currentLevel, " added at ", currentPrice, " Lot: ", lotSize);
      }
   }
   
   //+------------------------------------------------------------------+
   //| Check if profit target reached                                    |
   //+------------------------------------------------------------------+
   bool IsProfitTargetReached()
   {
      double totalProfit = 0;
      
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(position.SelectByIndex(i))
         {
            if(position.Symbol() == m_symbol && position.Magic() == m_magicNumber)
            {
               totalProfit += position.Profit() + position.Swap() + position.Commission();
            }
         }
      }
      
      if(totalProfit >= m_profitTarget)
      {
         Print("Grid profit target reached: $", totalProfit);
         return true;
      }
      
      return false;
   }
   
   //+------------------------------------------------------------------+
   //| Close all grid positions                                          |
   //+------------------------------------------------------------------+
   void CloseAllGridPositions()
   {
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(position.SelectByIndex(i))
         {
            if(position.Symbol() == m_symbol && position.Magic() == m_magicNumber)
            {
               trade.PositionClose(position.Symbol());
            }
         }
      }
      
      // Reset grid
      m_isActive = false;
      m_currentLevel = 0;
      m_totalVolume = 0;
      m_firstOrderPrice = 0;
      
      Print("All grid positions closed. Grid reset.");
   }
   
   //+------------------------------------------------------------------+
   //| Check drawdown limit                                              |
   //+------------------------------------------------------------------+
   bool CheckDrawdownLimit()
   {
      CAccountInfo account;
      double balance = account.Balance();
      double equity = account.Equity();
      
      if(balance > 0)
      {
         double drawdown = ((balance - equity) / balance) * 100;
         if(drawdown >= m_maxDrawdownPercent)
         {
            Print("Grid drawdown limit reached: ", drawdown, "%");
            CloseAllGridPositions();
            return false;
         }
      }
      
      return true;
   }
   
   //+------------------------------------------------------------------+
   //| Get first position type (buy or sell)                             |
   //+------------------------------------------------------------------+
   bool GetFirstPositionType()
   {
      // Assume first position in grid is the direction
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(position.SelectByIndex(i))
         {
            if(position.Symbol() == m_symbol && position.Magic() == m_magicNumber)
            {
               return (position.Type() == POSITION_TYPE_BUY);
            }
         }
      }
      return true; // Default to buy
   }
   
   //+------------------------------------------------------------------+
   //| Normalize lot size                                                |
   //+------------------------------------------------------------------+
   double NormalizeLotSize(double lotSize)
   {
      double minLot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
      double maxLot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MAX);
      double lotStep = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
      
      lotSize = MathFloor(lotSize / lotStep) * lotStep;
      lotSize = MathMax(lotSize, minLot);
      lotSize = MathMin(lotSize, maxLot);
      
      return lotSize;
   }
   
   //+------------------------------------------------------------------+
   //| Get grid statistics                                               |
   //+------------------------------------------------------------------+
   string GetGridStats()
   {
      double totalProfit = 0;
      int posCount = 0;
      
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(position.SelectByIndex(i))
         {
            if(position.Symbol() == m_symbol && position.Magic() == m_magicNumber)
            {
               totalProfit += position.Profit() + position.Swap() + position.Commission();
               posCount++;
            }
         }
      }
      
      string stats = StringFormat(
         "Grid: Level=%d/%d, Positions=%d, TotalLot=%.2f, Profit=$%.2f",
         m_currentLevel, m_maxGridLevels, posCount, m_totalVolume, totalProfit
      );
      return stats;
   }
   
   //+------------------------------------------------------------------+
   //| Set grid parameters                                               |
   //+------------------------------------------------------------------+
   void SetGridParameters(double gridSize, int maxLevels, double lotMultiplier)
   {
      m_gridSize = gridSize;
      m_maxGridLevels = maxLevels;
      m_lotMultiplier = lotMultiplier;
   }
   
   void SetRiskParameters(double maxDD, double profitTarget)
   {
      m_maxDrawdownPercent = maxDD;
      m_profitTarget = profitTarget;
   }
};
```

**IMPORTANT - Grid Trading Guidelines:**
1. **DO NOT use lot multiplier > 1.5** - Very dangerous!
2. **ALWAYS set max grid levels** - Never unlimited
3. **MUST set max drawdown** - Primary protection
4. **Use in ranging markets** - Not trending markets
5. **Test in demo MINIMUM 3 months** - Seriously!

---

### 4. MARTINGALE SYSTEM (ULTRA SAFE VERSION)

Pure martingale is SUICIDE. This is a much safer version with extensive protections.

```mql5
//+------------------------------------------------------------------+
//| Ultra Safe Martingale System                                       |
//+------------------------------------------------------------------+
class CSafeMartingale
{
private:
   string            m_symbol;
   int               m_magicNumber;
   
   double            m_baseLot;
   double            m_multiplier;            // Lot multiplier after loss (keep < 2.0!)
   int               m_maxSteps;              // Max martingale steps
   
   double            m_maxDrawdownPercent;
   double            m_profitTarget;
   double            m_stopLossPoints;
   double            m_takeProfitPoints;
   
   int               m_currentStep;
   double            m_currentLot;
   bool              m_isActive;
   
   int               m_consecutiveLosses;
   int               m_totalLosses;
   int               m_totalWins;
   
   CTrade            trade;
   CPositionInfo     position;

public:
   CSafeMartingale(string symbol, int magic, double baseLot, double multiplier, int maxSteps)
   {
      m_symbol = symbol;
      m_magicNumber = magic;
      m_baseLot = baseLot;
      m_multiplier = MathMin(multiplier, 2.0); // Force cap at 2.0!
      m_maxSteps = MathMin(maxSteps, 5); // Force cap at 5 steps!
      
      m_maxDrawdownPercent = 10.0; // STRICT limit
      m_profitTarget = 50.0;
      m_stopLossPoints = 50;
      m_takeProfitPoints = 50;
      
      m_currentStep = 0;
      m_currentLot = baseLot;
      m_isActive = false;
      
      m_consecutiveLosses = 0;
      m_totalLosses = 0;
      m_totalWins = 0;
      
      trade.SetExpertMagicNumber(magic);
      
      Print("!!! WARNING: Martingale system initialized !!!");
      Print("Multiplier: ", m_multiplier, " Max Steps: ", m_maxSteps);
      Print("NEVER use Martingale on real account without extensive testing!");
   }
   
   //+------------------------------------------------------------------+
   //| Open martingale trade                                             |
   //+------------------------------------------------------------------+
   bool OpenTrade(bool isBuy)
   {
      // Safety checks
      if(!CanTrade()) return false;
      
      double price = isBuy ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) : 
                             SymbolInfoDouble(m_symbol, SYMBOL_BID);
      double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
      
      // Calculate SL and TP
      double sl = 0, tp = 0;
      if(isBuy)
      {
         sl = price - (m_stopLossPoints * point);
         tp = price + (m_takeProfitPoints * point);
      }
      else
      {
         sl = price + (m_stopLossPoints * point);
         tp = price - (m_takeProfitPoints * point);
      }
      
      // Calculate lot size
      double lotSize = CalculateLotSize();
      
      // Open trade
      bool success = false;
      string comment = "Martingale Step " + IntegerToString(m_currentStep);
      
      if(isBuy)
         success = trade.Buy(lotSize, m_symbol, price, sl, tp, comment);
      else
         success = trade.Sell(lotSize, m_symbol, price, sl, tp, comment);
      
      if(success)
      {
         m_isActive = true;
         Print("Martingale trade opened: Step ", m_currentStep, " Lot: ", lotSize);
      }
      
      return success;
   }
   
   //+------------------------------------------------------------------+
   //| Calculate lot size for current step                               |
   //+------------------------------------------------------------------+
   double CalculateLotSize()
   {
      double lotSize = m_baseLot * MathPow(m_multiplier, m_currentStep);
      
      // Normalize
      double minLot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
      double maxLot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MAX);
      double lotStep = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
      
      lotSize = MathFloor(lotSize / lotStep) * lotStep;
      lotSize = MathMax(lotSize, minLot);
      lotSize = MathMin(lotSize, maxLot);
      
      return lotSize;
   }
   
   //+------------------------------------------------------------------+
   //| Handle trade result                                               |
   //+------------------------------------------------------------------+
   void OnTradeResult(bool isWin, double profit)
   {
      if(isWin)
      {
         // Win - reset martingale
         m_currentStep = 0;
         m_consecutiveLosses = 0;
         m_totalWins++;
         m_isActive = false;
         
         Print("Martingale WIN! Profit: $", profit, " - Sequence reset");
      }
      else
      {
         // Loss - increase step
         m_currentStep++;
         m_consecutiveLosses++;
         m_totalLosses++;
         m_isActive = false; // Allow next trade after loss
         
         if(m_currentStep >= m_maxSteps)
         {
            // Max steps reached - STOP!
            Print("!!! MARTINGALE MAX STEPS REACHED !!!");
            Print("Total losses: ", m_consecutiveLosses);
            Print("Stopping martingale sequence!");
            
            m_currentStep = 0;
            m_consecutiveLosses = 0;
            
            // Optional: Pause trading for a while
            // SetPauseUntil(TimeCurrent() + 3600); // 1 hour pause
         }
         else
         {
            Print("Martingale LOSS. Moving to step ", m_currentStep);
         }
      }
   }
   
   //+------------------------------------------------------------------+
   //| Check if can trade                                                |
   //+------------------------------------------------------------------+
   bool CanTrade()
   {
      CAccountInfo account;
      
      // Check if sequence is active
      if(m_isActive)
      {
         Print("Martingale sequence already active");
         return false;
      }
      
      // Check max steps
      if(m_currentStep >= m_maxSteps)
      {
         Print("Max martingale steps reached");
         return false;
      }
      
      // Check drawdown
      double balance = account.Balance();
      double equity = account.Equity();
      double drawdown = ((balance - equity) / balance) * 100;
      
      if(drawdown >= m_maxDrawdownPercent)
      {
         Print("Max drawdown reached: ", drawdown, "%");
         m_currentStep = 0;
         m_consecutiveLosses = 0;
         return false;
      }
      
      // Check if account can afford next step
      double nextLot = CalculateLotSize();
      double requiredMargin = 0;
      
      if(!OrderCalcMargin(ORDER_TYPE_BUY, m_symbol, nextLot, 
                          SymbolInfoDouble(m_symbol, SYMBOL_ASK), requiredMargin))
      {
         Print("Failed to calculate margin");
         return false;
      }
      
      double freeMargin = account.FreeMargin();
      if(requiredMargin > freeMargin * 0.5) // Use max 50% of free margin
      {
         Print("Insufficient margin for next martingale step");
         Print("Required: ", requiredMargin, " Available: ", freeMargin);
         m_currentStep = 0;
         return false;
      }
      
      // Stop after 3 consecutive losses in martingale
      if(m_consecutiveLosses >= 3)
      {
         Print("Too many consecutive losses: ", m_consecutiveLosses);
         Print("Pausing martingale system");
         m_currentStep = 0;
         m_consecutiveLosses = 0;
         return false;
      }
      
      return true;
   }
   
   //+------------------------------------------------------------------+
   //| Get martingale statistics                                         |
   //+------------------------------------------------------------------+
   string GetStats()
   {
      double winRate = 0;
      if(m_totalWins + m_totalLosses > 0)
         winRate = (double)m_totalWins / (m_totalWins + m_totalLosses) * 100;
      
      string stats = StringFormat(
         "Martingale: Step=%d/%d, ConsecLoss=%d, Wins=%d, Losses=%d, WinRate=%.1f%%, NextLot=%.2f",
         m_currentStep, m_maxSteps, m_consecutiveLosses,
         m_totalWins, m_totalLosses, winRate, CalculateLotSize()
      );
      return stats;
   }
   
   //+------------------------------------------------------------------+
   //| Reset martingale sequence                                         |
   //+------------------------------------------------------------------+
   void Reset()
   {
      m_currentStep = 0;
      m_consecutiveLosses = 0;
      m_isActive = false;
      Print("Martingale sequence manually reset");
   }
   
   //+------------------------------------------------------------------+
   //| Get maximum possible loss in sequence                             |
   //+------------------------------------------------------------------+
   double GetMaxPossibleLoss()
   {
      double totalLoss = 0;
      for(int i = 0; i <= m_maxSteps; i++)
      {
         double lot = m_baseLot * MathPow(m_multiplier, i);
         totalLoss += lot * m_stopLossPoints * SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_VALUE) / 
                      SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_SIZE) * 
                      SymbolInfoDouble(m_symbol, SYMBOL_POINT);
      }
      return totalLoss;
   }
};
```

**CRITICAL MARTINGALE WARNINGS:**

⚠️ **MARTINGALE DANGERS:**
1. **Can wipe out account in minutes**
2. **High win rate but one loss can destroy all profits**
3. **No real edge, just betting against probability**
4. **Brokers may ban due to suspicious activity**

✅ **IF YOU MUST USE (NOT RECOMMENDED):**
1. **Max multiplier: 1.5** (NEVER 2.0 or higher!)
2. **Max steps: 3-4** (NEVER 5+)
3. **Max drawdown: 10%** (STRICT)
4. **Test in demo minimum 6 months**
5. **Use ONLY in low volatility pairs** (EUR/USD, not GBP/JPY)
6. **Use ONLY in ranging markets**
7. **Prepare mentally for 100% loss** - Because it can happen

---

## BACKTESTING & OPTIMIZATION

### Strategy Tester Best Practices

```mql5
//+------------------------------------------------------------------+
//| Backtesting Guidelines                                             |
//+------------------------------------------------------------------+

// 1. MINIMUM DATA REQUIREMENTS
// - Minimum 1 year data for initial test
// - Minimum 3-5 years for validation
// - Test across various market conditions (trend, range, high volatility, low volatility)

// 2. OPTIMIZATION PARAMETERS
// - Don't optimize too many parameters (max 3-4)
// - Use walk-forward optimization
// - Validate on out-of-sample data

// 3. KEY METRICS TO TRACK
// - Profit Factor > 1.5 (minimum)
// - Win Rate: 40-60% (sweet spot)
// - Max Drawdown < 20%
// - Recovery Factor > 3
// - Sharpe Ratio > 1.0

// 4. OVERFITTING DETECTION
// - Compare in-sample vs out-of-sample results
// - If out-of-sample performance drops > 30%, likely overfitted
// - Use more robust parameters (less precise = more stable)

// 5. FORWARD TESTING
// - Test di demo account minimum 3 bulan
// - Monitor slippage and execution quality
// - Compare live vs backtest results

//+------------------------------------------------------------------+
//| Backtesting Validation Class                                       |
//+------------------------------------------------------------------+
class CBacktestValidator
{
private:
   int               m_totalTrades;
   int               m_winningTrades;
   int               m_losingTrades;
   
   double            m_grossProfit;
   double            m_grossLoss;
   double            m_netProfit;
   
   double            m_maxDrawdown;
   double            m_maxDrawdownPercent;
   
   double            m_largestWin;
   double            m_largestLoss;
   double            m_avgWin;
   double            m_avgLoss;
   
   datetime          m_startTime;
   datetime          m_endTime;
   double            m_initialBalance;

public:
   CBacktestValidator()
   {
      // Capture initial balance at construction
      CAccountInfo account;
      m_initialBalance = account.Balance();
      m_startTime = TimeCurrent();
      Reset();
   }
   
   void Reset()
   {
      m_totalTrades = 0;
      m_winningTrades = 0;
      m_losingTrades = 0;
      m_grossProfit = 0;
      m_grossLoss = 0;
      m_netProfit = 0;
      m_maxDrawdown = 0;
      m_maxDrawdownPercent = 0;
      m_largestWin = 0;
      m_largestLoss = 0;
      m_avgWin = 0;
      m_avgLoss = 0;
   }
   
   //+------------------------------------------------------------------+
   //| Calculate all statistics from history                             |
   //+------------------------------------------------------------------+
   void CalculateStats()
   {
      Reset();
      
      // Initial balance already captured in constructor
      // No need to re-assign here
      
      // Get all closed positions from history
      HistorySelect(m_startTime, TimeCurrent());
      
      int totalDeals = HistoryDealsTotal();
      
      double runningBalance = m_initialBalance;
      double peakBalance = m_initialBalance;
      
      for(int i = 0; i < totalDeals; i++)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0)
         {
            long dealEntry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
            
            // Only process EXIT deals (position close)
            if(dealEntry == DEAL_ENTRY_OUT || dealEntry == DEAL_ENTRY_OUT_BY)
            {
               double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
               double commission = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
               double swap = HistoryDealGetDouble(ticket, DEAL_SWAP);
               
               double netResult = profit + commission + swap;
               
               if(netResult != 0) // Ignore zero profit trades
               {
                  m_totalTrades++;
                  m_netProfit += netResult;
                  runningBalance += netResult;
                  
                  if(netResult > 0)
                  {
                     m_winningTrades++;
                     m_grossProfit += netResult;
                     m_avgWin += netResult;
                     
                     if(netResult > m_largestWin)
                        m_largestWin = netResult;
                  }
                  else
                  {
                     m_losingTrades++;
                     m_grossLoss += netResult;
                     m_avgLoss += netResult;
                     
                     if(netResult < m_largestLoss)
                        m_largestLoss = netResult;
                  }
                  
                  // Track drawdown
                  if(runningBalance > peakBalance)
                     peakBalance = runningBalance;
                  
                  double currentDD = peakBalance - runningBalance;
                  if(currentDD > m_maxDrawdown)
                  {
                     m_maxDrawdown = currentDD;
                     m_maxDrawdownPercent = (currentDD / peakBalance) * 100;
                  }
               }
            }
         }
      }
      
      // Calculate averages
      if(m_winningTrades > 0)
         m_avgWin /= m_winningTrades;
      if(m_losingTrades > 0)
         m_avgLoss /= m_losingTrades;
   }
   
   //+------------------------------------------------------------------+
   //| Get profit factor                                                 |
   //+------------------------------------------------------------------+
   double GetProfitFactor()
   {
      if(m_grossLoss == 0) return 0;
      return m_grossProfit / MathAbs(m_grossLoss);
   }
   
   //+------------------------------------------------------------------+
   //| Get win rate                                                      |
   //+------------------------------------------------------------------+
   double GetWinRate()
   {
      if(m_totalTrades == 0) return 0;
      return (double)m_winningTrades / m_totalTrades * 100;
   }
   
   //+------------------------------------------------------------------+
   //| Get recovery factor                                               |
   //+------------------------------------------------------------------+
   double GetRecoveryFactor()
   {
      if(m_maxDrawdown == 0) return 0;
      return m_netProfit / m_maxDrawdown;
   }
   
   //+------------------------------------------------------------------+
   //| Get average win/loss ratio                                        |
   //+------------------------------------------------------------------+
   double GetWinLossRatio()
   {
      if(m_avgLoss == 0) return 0;
      return m_avgWin / MathAbs(m_avgLoss);
   }
   
   //+------------------------------------------------------------------+
   //| Get Sharpe Ratio (simplified)                                     |
   //+------------------------------------------------------------------+
   double GetSharpeRatio()
   {
      if(m_totalTrades < 2) return 0;
      
      // Calculate standard deviation of returns
      HistorySelect(m_startTime, TimeCurrent());
      int totalDeals = HistoryDealsTotal();
      
      double returns[];
      ArrayResize(returns, 0);
      
      for(int i = 0; i < totalDeals; i++)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0)
         {
            long dealEntry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
            
            // Only count EXIT deals
            if(dealEntry == DEAL_ENTRY_OUT || dealEntry == DEAL_ENTRY_OUT_BY)
            {
               double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) +
                             HistoryDealGetDouble(ticket, DEAL_COMMISSION) +
                             HistoryDealGetDouble(ticket, DEAL_SWAP);
               
               if(profit != 0)
               {
                  int size = ArraySize(returns);
                  ArrayResize(returns, size + 1);
                  returns[size] = profit;
               }
            }
         }
      }
      
      // Guard against empty array
      if(ArraySize(returns) < 2) return 0;
      
      // Calculate mean return
      double meanReturn = 0;
      for(int i = 0; i < ArraySize(returns); i++)
         meanReturn += returns[i];
      meanReturn /= ArraySize(returns);
      
      // Calculate standard deviation
      double variance = 0;
      for(int i = 0; i < ArraySize(returns); i++)
      {
         double diff = returns[i] - meanReturn;
         variance += diff * diff;
      }
      variance /= (ArraySize(returns) - 1);
      double stdDev = MathSqrt(variance);
      
      if(stdDev == 0) return 0;
      
      // Sharpe Ratio = Mean Return / Std Deviation
      return meanReturn / stdDev;
   }
   
   //+------------------------------------------------------------------+
   //| Print comprehensive report                                         |
   //+------------------------------------------------------------------+
   void PrintReport()
   {
      Print("========================================");
      Print("BACKTEST VALIDATION REPORT");
      Print("========================================");
      Print("Total Trades: ", m_totalTrades);
      Print("Winning Trades: ", m_winningTrades, " (", GetWinRate(), "%)");
      Print("Losing Trades: ", m_losingTrades);
      Print("----------------------------------------");
      Print("Net Profit: $", m_netProfit);
      Print("Gross Profit: $", m_grossProfit);
      Print("Gross Loss: $", m_grossLoss);
      Print("Profit Factor: ", GetProfitFactor());
      Print("----------------------------------------");
      Print("Average Win: $", m_avgWin);
      Print("Average Loss: $", m_avgLoss);
      Print("Win/Loss Ratio: ", GetWinLossRatio());
      Print("Largest Win: $", m_largestWin);
      Print("Largest Loss: $", m_largestLoss);
      Print("----------------------------------------");
      Print("Max Drawdown: $", m_maxDrawdown, " (", m_maxDrawdownPercent, "%)");
      Print("Recovery Factor: ", GetRecoveryFactor());
      Print("Sharpe Ratio: ", GetSharpeRatio());
      Print("----------------------------------------");
      
      // Provide assessment
      Print("ASSESSMENT:");
      
      bool passed = true;
      
      if(GetProfitFactor() < 1.5)
      {
         Print("❌ Profit Factor too low (< 1.5)");
         passed = false;
      }
      else
         Print("✓ Profit Factor acceptable");
      
      if(GetWinRate() < 35 || GetWinRate() > 70)
      {
         Print("⚠ Win Rate outside optimal range (35-70%)");
      }
      else
         Print("✓ Win Rate in good range");
      
      if(m_maxDrawdownPercent > 20)
      {
         Print("❌ Max Drawdown too high (> 20%)");
         passed = false;
      }
      else
         Print("✓ Max Drawdown acceptable");
      
      if(GetRecoveryFactor() < 3)
      {
         Print("❌ Recovery Factor too low (< 3)");
         passed = false;
      }
      else
         Print("✓ Recovery Factor acceptable");
      
      if(GetSharpeRatio() < 1.0)
      {
         Print("⚠ Sharpe Ratio could be better (< 1.0)");
      }
      else
         Print("✓ Sharpe Ratio good");
      
      if(m_totalTrades < 100)
      {
         Print("⚠ Sample size small (< 100 trades)");
      }
      else
         Print("✓ Sample size adequate");
      
      Print("========================================");
      
      if(passed)
         Print("✓ STRATEGY PASSED VALIDATION");
      else
         Print("❌ STRATEGY FAILED VALIDATION - DO NOT USE ON REAL ACCOUNT");
      
      Print("========================================");
   }
   
   //+------------------------------------------------------------------+
   //| Is strategy acceptable?                                           |
   //+------------------------------------------------------------------+
   bool IsStrategyAcceptable()
   {
      if(m_totalTrades < 50) return false; // Too few trades
      if(GetProfitFactor() < 1.5) return false;
      if(m_maxDrawdownPercent > 20) return false;
      if(GetRecoveryFactor() < 3) return false;
      
      return true;
   }
};
```

---

## PRE-DEPLOYMENT CHECKLIST

### ✅ Before Going Live

```
TESTING PHASE:
□ Backtest minimum 3 years with quality data
□ Profit factor > 1.5
□ Max drawdown < 20%
□ Recovery factor > 3
□ Minimum 100 trades in backtest
□ Win rate 40-60% (sustainable range)
□ Test in various market conditions (trend, range, high vol, low vol)

DEMO TRADING:
□ Demo trading minimum 3 months
□ Compare backtest vs demo results (difference < 30%)
□ Monitor slippage and execution quality
□ Test all features (BE, trailing, daily limits)
□ Verify no errors in log

RISK MANAGEMENT:
□ Set max risk per trade <= 1%
□ Set max daily loss <= 5%
□ Set max drawdown <= 20%
□ Enable all protective stops
□ Document worst-case scenario loss

CODE QUALITY:
□ No errors in compilation
□ No critical warnings
□ Error handling for all trade operations
□ Logging for debug purposes
□ Magic number unique
□ Code commented and documented

BROKER REQUIREMENTS:
□ Verify broker allows EA trading
□ Check spread requirements
□ Confirm execution speed acceptable
□ Verify no restrictions on trading strategy
□ Check margin requirements

PSYCHOLOGICAL PREPARATION:
□ Ready to see 10-20% drawdown
□ Won't panic close EA during losses
□ Won't interfere with EA trades
□ Have exit strategy if performance drops
□ Prepared for worst case (total loss of capital)

MONITORING SETUP:
□ Setup notification system (email/telegram)
□ Daily performance tracking
□ Weekly analysis and review
□ Monthly reoptimization schedule
□ Emergency stop procedure documented
```

---

## SURVIVAL TIPS FOR REAL MARKET

### 1. **Start VERY Small**
- Start with minimum account (not all capital)
- Risk per trade: 0.5% (not 1%)
- Scale up ONLY after 6 months profitable

### 2. **Monitor Like Your Life Depends On It** (Because it does!)
- Check EA performance DAILY
- Review trades WEEKLY
- Re-backtest MONTHLY
- Re-optimize QUARTERLY

### 3. **Adapt to Market Changes**
- Markets change - EAs must be updated
- If performance drops 30%+ from backtest → STOP and analyze
- Don't be stubborn with strategies that don't work

### 4. **Mental Game**
- Drawdown is NORMAL - don't panic
- 10 consecutive losses can happen - be mentally prepared
- Greed will kill your account - stick to the plan
- FOMO is the enemy - don't overtrade

### 5. **Continuous Learning**
- Market Microstructure
- Order Flow Analysis
- Liquidity Patterns
- News Impact
- Correlation Trading

---

## ADVANCED CONCEPTS (Beyond Basic EA)

### Machine Learning Integration (Simplified)

For ML in MQL5, the concept is:
1. **Feature Engineering** - Collect market data (MA, RSI, Volume, Volatility)
2. **Train Model** - Use Python/R for training
3. **Export Model** - Convert to format that MQL5 can read
4. **Inference** - EA predicts using the model

**Simple ML Feature Collection Example:**
```mql5
//+------------------------------------------------------------------+
//| Collect features for ML                                           |
//+------------------------------------------------------------------+

// Global indicator handles (create in OnInit)
int handleFastMA, handleSlowMA, handleRSI, handleATR, handleBB;
double maFastBuffer[], maSlowBuffer[], rsiBuffer[], atrBuffer[];
double bbUpperBuffer[], bbLowerBuffer[], bbMiddleBuffer[];

int OnInit()
{
   // Create indicator handles once
   handleFastMA = iMA(_Symbol, PERIOD_CURRENT, 10, 0, MODE_EMA, PRICE_CLOSE);
   handleSlowMA = iMA(_Symbol, PERIOD_CURRENT, 30, 0, MODE_EMA, PRICE_CLOSE);
   handleRSI = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
   handleATR = iATR(_Symbol, PERIOD_CURRENT, 14);
   handleBB = iBands(_Symbol, PERIOD_CURRENT, 20, 0, 2, PRICE_CLOSE);
   
   // Set arrays as series
   ArraySetAsSeries(maFastBuffer, true);
   ArraySetAsSeries(maSlowBuffer, true);
   ArraySetAsSeries(rsiBuffer, true);
   ArraySetAsSeries(atrBuffer, true);
   ArraySetAsSeries(bbUpperBuffer, true);
   ArraySetAsSeries(bbLowerBuffer, true);
   ArraySetAsSeries(bbMiddleBuffer, true);
   
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   // Release indicator handles
   if(handleFastMA != INVALID_HANDLE) IndicatorRelease(handleFastMA);
   if(handleSlowMA != INVALID_HANDLE) IndicatorRelease(handleSlowMA);
   if(handleRSI != INVALID_HANDLE) IndicatorRelease(handleRSI);
   if(handleATR != INVALID_HANDLE) IndicatorRelease(handleATR);
   if(handleBB != INVALID_HANDLE) IndicatorRelease(handleBB);
}

// Collect features - pass by reference
void CollectFeatures(double &features[], int shift = 0)
{
   ArrayResize(features, 9); // 9 features (not 10)
   
   // Copy indicator values
   if(CopyBuffer(handleFastMA, 0, shift, 1, maFastBuffer) <= 0) return;
   if(CopyBuffer(handleSlowMA, 0, shift, 1, maSlowBuffer) <= 0) return;
   if(CopyBuffer(handleRSI, 0, shift, 1, rsiBuffer) <= 0) return;
   if(CopyBuffer(handleATR, 0, shift, 1, atrBuffer) <= 0) return;
   if(CopyBuffer(handleBB, 0, shift, 1, bbUpperBuffer) <= 0) return;
   if(CopyBuffer(handleBB, 1, shift, 1, bbMiddleBuffer) <= 0) return;
   if(CopyBuffer(handleBB, 2, shift, 1, bbLowerBuffer) <= 0) return;
   
   double fastMA = maFastBuffer[0];
   double slowMA = maSlowBuffer[0];
   double currentClose = iClose(_Symbol, PERIOD_CURRENT, shift);
   
   // Feature 0-1: MA values (with safety check)
   if(slowMA != 0)
      features[0] = (fastMA - slowMA) / slowMA; // Normalized difference
   else
      features[0] = 0;
   
   if(fastMA != 0)
      features[1] = (currentClose - fastMA) / fastMA;
   else
      features[1] = 0;
   
   // Feature 2: RSI (normalized around 50)
   double rsi = rsiBuffer[0];
   features[2] = (rsi - 50) / 50;
   
   // Feature 3: ATR (Volatility)
   double atr = atrBuffer[0];
   double avgPrice = (iHigh(_Symbol, PERIOD_CURRENT, shift) + iLow(_Symbol, PERIOD_CURRENT, shift)) / 2;
   if(avgPrice != 0)
      features[3] = atr / avgPrice; // Normalized volatility
   else
      features[3] = 0;
   
   // Feature 4: Volume
   long volume = iVolume(_Symbol, PERIOD_CURRENT, shift);
   long avgVolume = 0;
   for(int i = 1; i <= 20; i++)
      avgVolume += iVolume(_Symbol, PERIOD_CURRENT, shift + i);
   avgVolume /= 20;
   
   if(avgVolume != 0)
      features[4] = (double)(volume - avgVolume) / avgVolume;
   else
      features[4] = 0;
   
   // Feature 5-6: Price momentum (with bar existence check)
   if(Bars(_Symbol, PERIOD_CURRENT) > shift + 20)
   {
      double price5 = iClose(_Symbol, PERIOD_CURRENT, shift + 5);
      double price20 = iClose(_Symbol, PERIOD_CURRENT, shift + 20);
      
      if(price5 != 0)
         features[5] = (currentClose - price5) / price5;
      else
         features[5] = 0;
      
      if(price20 != 0)
         features[6] = (currentClose - price20) / price20;
      else
         features[6] = 0;
   }
   else
   {
      features[5] = 0;
      features[6] = 0;
   }
   
   // Feature 7: Bollinger Band position
   double bbUpper = bbUpperBuffer[0];
   double bbLower = bbLowerBuffer[0];
   double bbWidth = bbUpper - bbLower;
   
   if(bbWidth > 0)
      features[7] = (currentClose - bbLower) / bbWidth;
   else
      features[7] = 0.5;
   
   // Feature 8: Time of day (normalized)
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   features[8] = (double)dt.hour / 24.0;
}

// Usage in OnTick
void OnTick()
{
   double features[];
   CollectFeatures(features, 0); // Get features for current bar
   
   // Now use features[] for ML prediction
   // ...
}
```

---

## CONCLUSION

A good EA is NOT one that makes 1000% profit in a month. A good EA is one that:
1. **Survives** - Doesn't go bankrupt
2. **Consistent** - Steady profit, not spikes
3. **Robust** - Works in various market conditions
4. **Simple** - Complex != Better
5. **Tested** - Thousands of hours in backtesting and demo

**Remember:**
- 90% of traders fail not because of bad strategy, but because of POOR RISK MANAGEMENT
- EA is just a tool - not a money machine
- Markets don't owe you anything - respect the market
- Survival > Profit

Good luck, trade safe, and never risk money you can't afford to lose! 🚀

---

## WHEN TO USE THIS SKILL

This skill should be used when:
- User wants to create a new Expert Advisor from scratch
- User wants to optimize existing trading strategy
- User needs help with advanced MQL5 concepts (grid, martingale, MTF)
- User wants professional money management implementation
- User needs backtesting and validation guidance
- User asks about survival strategies for live trading
- User wants to convert trading idea into code

**AI-Specific Notes:**
- **Claude:** Will automatically reference this skill from skills directory
- **ChatGPT:** Use as Custom GPT knowledge base or system instructions
- **Gemini:** Include in conversation context or as extension data
- **Other AI:** Provide relevant sections in prompt/context

Always prioritize:
1. Risk management over profit maximization
2. Robustness over complexity
3. Testing over deployment
4. Capital preservation over returns

Focus on creating EA that can SURVIVE, not just EA that look good in backtest.
