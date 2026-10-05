# Protective Hedge — Reference Implementation (Section 5.13)

Arm-then-trigger protective hedge for MT5 **hedging accounts**. Read Section 5.13 in `SKILL.md` for the rule summary; this file holds the complete, compilable module.

## Rule

| Step | Buy entry (sell entry is the mirror image) |
|---|---|
| 1. Arm | Entry starts **unarmed**. It arms once **Bid > entry + `InpHedgeArmBufferPips`**. A fresh entry can therefore never be hedged by the spread alone. |
| 2. Trigger | Once armed, when **Bid ≤ entry − `InpHedgeTriggerPips`**, open an opposite SELL hedge and **disarm** the entry. One active hedge per entry. |
| 3. Hedge lot | **Original** entry lot × `InpHedgeLotMult` (hard cap 1.5), rounded **down** to the lot step. Below broker minimum → skip (never round up). |
| 4. Hedge TP | Entry SL. |
| 5. Hedge SL (backstop) | Entry + `InpBE_TriggerPips` + `InpHedgeSLBufferPips`. Only a safety net — the EA normally closes the hedge first (step 6). |
| 6. EA closes the hedge | On the first tick that the entry **reaches break-even** (entry SL at/beyond entry price) **or closes** (SL, TP, manual). Removes the spread gap between the two legs. |
| 7. Hedge break-even | Once the hedge is `InpHedgeBEPips` in profit, its SL moves to its own open price (0 = off). |
| 8. Re-arm | After a hedge, the **same rule as step 1** re-arms the entry. |

Hedges are never blocked by entry filters (session, spread, daily halt) — they only reduce risk. They carry their own magic, so entry position counts, break-even and partials ignore them.

## Requirements from the host EA

- `InpMagicNumber` (entry magic), `InpSlippage` (points), `InpBE_TriggerPips` (Section 5.9).
- An entry break-even manager (Section 5.9) that runs **before** `ManageHedges()` in `OnTick`, so a break-even set on a tick closes the hedge on the same tick.
- `HedgePip()` must use the **same pip conversion** as the break-even manager (Section 5.9 uses `_Point * 10`), or the backstop SL drifts away from the break-even level.
- If the EA takes partial closes, break-even must fire at or before the first partial. The hedge uses the ORIGINAL lot: that is safe because a break-even entry is never hedged, but a partial before break-even would make the hedge larger than the remaining entry.

## Module

```mql5
//+------------------------------------------------------------------+
//| Protective Hedge module — hedging accounts only                  |
//| Host EA provides: InpMagicNumber, InpSlippage, InpBE_TriggerPips |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>

input group "=== PROTECTIVE HEDGE (hedging accounts only) ==="
input bool   InpUseHedge           = false;   // Hedge entries that move against you
input double InpHedgeArmBufferPips = 0.0;     // Arm only after price trades this far beyond entry in profit
input double InpHedgeTriggerPips   = 1.0;     // Adverse pips from entry (once armed) before hedging
input double InpHedgeLotMult       = 1.0;     // Hedge lot = ORIGINAL entry lot x this (max 1.5)
input double InpHedgeSLBufferPips  = 10.0;    // Backstop SL = entry + BE trigger + this (> widest spread)
input double InpHedgeBEPips        = 20.0;    // Hedge profit before its SL moves to its own open price (0 = off)
input ulong  InpHedgeMagic         = 12346;   // Magic for hedge trades (MUST differ from InpMagicNumber)

#define HEDGE_MAX_LOT_MULT 1.5
#define HEDGE_RETRY_SEC    10                 // pause after a failed open/close before retrying
#define HEDGE_ARMED        2.0                // arm-flag value (flag absent = not armed)

CTrade   c_HedgeTrade;                        // dedicated object: hedges carry InpHedgeMagic
datetime g_HedgeRetryAt      = 0;
datetime g_HedgeCloseRetryAt = 0;

// Keep identical to the pip conversion of the entry break-even manager (Section 5.9)
double HedgePip()                  { return _Point * 10; }
double HedgePips(const double pips) { return pips * HedgePip(); }

//--- OnInit: validate inputs and set up the hedge CTrade. Returns false -> INIT_PARAMETERS_INCORRECT
bool InitHedge() {
    if(!InpUseHedge) return true;
    if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING) {
        Print("[ERROR] Hedge module requires a HEDGING account (an opposite order closes the entry on netting)");
        return false;
    }
    if(InpHedgeMagic == InpMagicNumber) {
        Print("[ERROR] InpHedgeMagic must differ from InpMagicNumber");
        return false;
    }
    if(InpHedgeTriggerPips <= 0 || InpHedgeLotMult <= 0 || InpHedgeBEPips < 0 ||
       InpHedgeSLBufferPips < 0 || InpHedgeArmBufferPips < 0) {
        Print("[ERROR] Hedge: trigger and lot multiplier must be > 0; other hedge pips must be >= 0");
        return false;
    }
    if(InpBE_TriggerPips <= 0) {
        Print("[ERROR] Hedge backstop SL is entry + InpBE_TriggerPips + buffer, so InpBE_TriggerPips must be > 0");
        return false;
    }
    if(InpHedgeLotMult > HEDGE_MAX_LOT_MULT)
        Print("[WARN] InpHedgeLotMult capped at ", DoubleToString(HEDGE_MAX_LOT_MULT, 1));
    if(InpHedgeArmBufferPips >= InpBE_TriggerPips)
        Print("[WARN] Arm buffer >= break-even trigger: break-even always fires first, no hedge will ever open");

    c_HedgeTrade.SetExpertMagicNumber(InpHedgeMagic);
    c_HedgeTrade.SetDeviationInPoints((ulong)InpSlippage);
    c_HedgeTrade.SetTypeFillingBySymbol(_Symbol);
    c_HedgeTrade.SetAsyncMode(false);
    c_HedgeTrade.LogLevel(LOG_LEVEL_ERRORS);
    return true;
}

//--- Hedge <-> entry link: comment "HEDGE#<entry ticket>"
string HedgeComment(const ulong ticket) { return "HEDGE#" + IntegerToString((long)ticket); }

ulong HedgeEntryTicket(const string comment) {
    if(StringFind(comment, "HEDGE#") != 0) return 0;
    return (ulong)StringToInteger(StringSubstr(comment, 6));
}

//--- Arm flag per entry: terminal global variable, survives EA reloads
string HedgeFlagPrefix() { return "HEDGE_" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "_"; }
string HedgeArmFlag(const ulong ticket) { return HedgeFlagPrefix() + IntegerToString((long)ticket); }

// Remove arm flags of entries that are no longer open
void CleanupHedgeFlags() {
    string prefix = HedgeFlagPrefix();
    for(int i = GlobalVariablesTotal() - 1; i >= 0; i--) {
        string name = GlobalVariableName(i);
        if(StringFind(name, prefix) != 0) continue;
        ulong ticket = (ulong)StringToInteger(StringSubstr(name, StringLen(prefix)));
        if(ticket > 0 && !PositionSelectByTicket(ticket)) GlobalVariableDel(name);
    }
}

// True if a hedge for this entry is open. Changes the selected position:
// call BEFORE PositionSelectByTicket(entry).
bool HasActiveHedge(const ulong ticket) {
    string cmt = HedgeComment(ticket);
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong t = PositionGetTicket(i);
        if(t == 0 || !PositionSelectByTicket(t)) continue;
        if((ulong)PositionGetInteger(POSITION_MAGIC) != InpHedgeMagic) continue;
        if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetString(POSITION_COMMENT) == cmt) return true;
    }
    return false;
}

// Original lot of a position = sum of its entry deals (partials do not change it)
double HedgeOriginalLot(const long posId, const double fallback) {
    if(!HistorySelectByPosition(posId)) return fallback;
    double vol = 0;
    for(int d = HistoryDealsTotal() - 1; d >= 0; d--) {
        ulong deal = HistoryDealGetTicket(d);
        if(deal > 0 && HistoryDealGetInteger(deal, DEAL_ENTRY) == DEAL_ENTRY_IN)
            vol += HistoryDealGetDouble(deal, DEAL_VOLUME);
    }
    return (vol > 0) ? vol : fallback;
}

// Triggered but not placed: log once, then pause before retrying
void HedgeSkip(const ulong ticket, const string reason) {
    g_HedgeRetryAt = TimeCurrent() + HEDGE_RETRY_SEC;
    Print("[HEDGE] #", ticket, " not hedged: ", reason, " - retry in ", HEDGE_RETRY_SEC, "s");
}

//--- Arm / trigger / open. Returns true only when a hedge was opened.
bool HedgePosition(const ulong ticket) {
    if(HasActiveHedge(ticket))          return false;     // one active hedge per entry
    if(!PositionSelectByTicket(ticket)) return false;

    bool   isBuy  = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
    double openPx = PositionGetDouble(POSITION_PRICE_OPEN);
    double entSL  = PositionGetDouble(POSITION_SL);
    double curVol = PositionGetDouble(POSITION_VOLUME);
    long   posId  = PositionGetInteger(POSITION_IDENTIFIER);

    // Needs an entry SL on the losing side (hedge TP = entry SL); at break-even there is nothing to hedge
    if(entSL <= 0 || (isBuy && entSL >= openPx) || (!isBuy && entSL <= openPx)) return false;

    MqlTick tick;
    if(!SymbolInfoTick(_Symbol, tick)) return false;
    double px = isBuy ? tick.bid : tick.ask;              // entry's closing side = hedge's fill side

    // 1) Arm (first time and after every hedge); never arm and fire on the same tick
    string flag = HedgeArmFlag(ticket);
    bool armed  = GlobalVariableCheck(flag) && GlobalVariableGet(flag) > HEDGE_ARMED - 0.5;
    if(!armed) {
        double armLevel = isBuy ? openPx + HedgePips(InpHedgeArmBufferPips)
                                : openPx - HedgePips(InpHedgeArmBufferPips);
        bool beyond = isBuy ? (px > armLevel) : (px < armLevel);
        if(beyond && GlobalVariableSet(flag, HEDGE_ARMED) > 0)
            Print("[HEDGE] Armed #", ticket, " at ", DoubleToString(px, _Digits));
        return false;
    }

    // 2) Trigger
    double trigger = HedgePips(InpHedgeTriggerPips);
    if(isBuy  && px > openPx - trigger) return false;
    if(!isBuy && px < openPx + trigger) return false;
    if(TimeCurrent() < g_HedgeRetryAt)  return false;
    if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED)) {
        HedgeSkip(ticket, "algo trading disabled");
        return false;
    }

    // 3) SL / TP: TP = entry SL, backstop SL = entry + BE trigger + buffer
    double slOff = HedgePips(InpBE_TriggerPips + InpHedgeSLBufferPips);
    double hTP   = NormalizeDouble(entSL, _Digits);
    double hSL   = NormalizeDouble(isBuy ? openPx + slOff : openPx - slOff, _Digits);
    double minDist = (double)MathMax(SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL),
                                     SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point;
    // The hedge's SL/TP trigger on ITS closing side: Ask for a sell hedge, Bid for a buy hedge
    double hClose = isBuy ? tick.ask : tick.bid;
    bool valid = isBuy ? (hClose - hTP >= minDist && hSL - hClose >= minDist)
                       : (hTP - hClose >= minDist && hClose - hSL >= minDist);
    if(!valid) { HedgeSkip(ticket, "SL/TP inside spread or broker stop/freeze level"); return false; }

    // 4) Lot: ORIGINAL entry lot x multiplier, rounded DOWN, never raised to the minimum
    double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    if(step <= 0) step = 0.01;
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lots   = MathFloor(HedgeOriginalLot(posId, curVol) * MathMin(InpHedgeLotMult, HEDGE_MAX_LOT_MULT)
                              / step + 1e-9) * step;
    if(lots < minLot - 1e-9) { HedgeSkip(ticket, "hedge lot below broker minimum"); return false; }
    int lotDigits = (int)MathMax(0, MathCeil(-MathLog10(step) - 1e-9));
    lots = NormalizeDouble(MathMin(lots, maxLot), lotDigits);

    // 5) Open, then disarm until price trades beyond the arm level again
    string cmt = HedgeComment(ticket);
    bool ok = isBuy ? c_HedgeTrade.Sell(lots, _Symbol, px, hSL, hTP, cmt)
                    : c_HedgeTrade.Buy(lots,  _Symbol, px, hSL, hTP, cmt);
    uint rc = c_HedgeTrade.ResultRetcode();
    if(!ok || (rc != TRADE_RETCODE_DONE && rc != TRADE_RETCODE_PLACED && rc != TRADE_RETCODE_DONE_PARTIAL)) {
        HedgeSkip(ticket, "order failed: " + c_HedgeTrade.ResultRetcodeDescription() + " | code " + IntegerToString(rc));
        return false;
    }
    if(!GlobalVariableDel(flag))
        Print("[WARN] Hedge arm flag not cleared for #", ticket, " - may re-hedge too early");
    Print("[ENTRY] HEDGE #", ticket, " -> ", (isBuy ? "SELL " : "BUY "), DoubleToString(lots, lotDigits),
          " @ ", DoubleToString(px, _Digits), " SL ", DoubleToString(hSL, _Digits), " TP ", DoubleToString(hTP, _Digits));
    return true;
}

//--- Move a hedge's SL to its own open price once it is InpHedgeBEPips in profit
void HedgeBreakEven(const ulong hTicket) {
    if(InpHedgeBEPips <= 0)              return;
    if(!PositionSelectByTicket(hTicket)) return;
    if((ulong)PositionGetInteger(POSITION_MAGIC) != InpHedgeMagic) return;

    bool   isSell = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL);
    double openPx = PositionGetDouble(POSITION_PRICE_OPEN);
    double curSL  = PositionGetDouble(POSITION_SL);
    double curTP  = PositionGetDouble(POSITION_TP);
    double beTrig = HedgePips(InpHedgeBEPips);
    double newSL  = NormalizeDouble(openPx, _Digits);
    double minDist = (double)MathMax(SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL),
                                     SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point;
    MqlTick tick;
    if(!SymbolInfoTick(_Symbol, tick)) return;

    if(isSell) {                                          // SELL hedge closes at Ask
        if(tick.ask > openPx - beTrig)                return;
        if(curSL > 0 && curSL <= newSL + _Point * 0.5) return;
        if(newSL - tick.ask < minDist)                return;
    } else {                                              // BUY hedge closes at Bid
        if(tick.bid < openPx + beTrig)                return;
        if(curSL >= newSL - _Point * 0.5)             return;
        if(tick.bid - newSL < minDist)                return;
    }
    if(c_HedgeTrade.PositionModify(hTicket, newSL, curTP) && c_HedgeTrade.ResultRetcode() == TRADE_RETCODE_DONE)
        Print("[BE] Hedge #", hTicket, " SL moved to break-even ", DoubleToString(newSL, _Digits));
    else
        Print("[ERROR] Hedge BE #", hTicket, " failed: ", c_HedgeTrade.ResultRetcodeDescription(),
              " | code ", c_HedgeTrade.ResultRetcode());
}

//--- Close hedges whose entry closed or reached break-even (SL at/beyond entry price)
void CloseFinishedHedges() {
    if(TimeCurrent() < g_HedgeCloseRetryAt) return;
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong hTicket = PositionGetTicket(i);
        if(hTicket == 0 || !PositionSelectByTicket(hTicket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if((ulong)PositionGetInteger(POSITION_MAGIC) != InpHedgeMagic) continue;
        ulong entry = HedgeEntryTicket(PositionGetString(POSITION_COMMENT));
        if(entry == 0) continue;                          // unreadable comment: leave to its own SL/TP

        string reason = "";
        if(!PositionSelectByTicket(entry))
            reason = "entry closed";
        else {
            bool   isBuy  = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
            double openPx = PositionGetDouble(POSITION_PRICE_OPEN);
            double entSL  = PositionGetDouble(POSITION_SL);
            if(entSL > 0 && (isBuy ? entSL >= openPx - _Point * 0.5 : entSL <= openPx + _Point * 0.5))
                reason = "entry reached break-even";
        }
        if(reason == "") continue;

        if(c_HedgeTrade.PositionClose(hTicket) &&
           (c_HedgeTrade.ResultRetcode() == TRADE_RETCODE_DONE || c_HedgeTrade.ResultRetcode() == TRADE_RETCODE_DONE_PARTIAL))
            Print("[HEDGE] Closed hedge #", hTicket, " for entry #", entry, ": ", reason);
        else {
            g_HedgeCloseRetryAt = TimeCurrent() + HEDGE_RETRY_SEC;
            Print("[ERROR] Closing hedge #", hTicket, " failed: ", c_HedgeTrade.ResultRetcodeDescription(),
                  " | code ", c_HedgeTrade.ResultRetcode(), " - retry in ", HEDGE_RETRY_SEC, "s");
            return;
        }
    }
}

//--- OnTick: every tick, AFTER the entry break-even manager
void ManageHedges() {
    if(!InpUseHedge) return;
    CloseFinishedHedges();                                // 0) entry closed / at break-even -> close hedge
    for(int i = PositionsTotal() - 1; i >= 0; i--) {      // 1) arm / trigger / open (new hedges append at the end)
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0 || !PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;
        HedgePosition(ticket);
    }
    for(int i = PositionsTotal() - 1; i >= 0; i--) {      // 2) hedge break-even
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0 || !PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if((ulong)PositionGetInteger(POSITION_MAGIC) != InpHedgeMagic) continue;
        HedgeBreakEven(ticket);
    }
    CleanupHedgeFlags();                                  // 3) drop arm flags of closed entries
}
```

## Wiring

```mql5
int OnInit() {
    // ... InitTrade() and the rest of the EA's validation ...
    if(!InitHedge()) return INIT_PARAMETERS_INCORRECT;
    return INIT_SUCCEEDED;
}

void OnTick() {
    // 1) entry management first: break-even (Section 5.9), partials, trailing
    // 2) then hedges, every tick (never only on a new bar), never behind entry filters
    ManageHedges();
    // 3) then signal / entry logic
}
```

Entry-side code must keep filtering positions by `InpMagicNumber` so hedges (`InpHedgeMagic`) are never counted as entries or given the entry's break-even and partials.

## Worked example

Buy at Ask 2650.00, SL 2644.90 (51 pips), gold with pip = 0.10, spread 5 pips, trigger 1, arm buffer 0, BE trigger 20, SL buffer 10, multiplier 1.0.

| Step | Price | Action |
|---|---|---|
| Entry | Ask 2650.00 / Bid 2649.50 | Not armed — the spread cannot trigger a hedge |
| Price rises | Bid > 2650.00 | Armed |
| Price falls | Bid 2649.90 | SELL hedge @ 2649.90, TP 2644.90, backstop SL 2653.00; entry disarmed |
| Then up to +20 | Bid 2652.00 | Entry break-even fires → EA closes hedge the same tick |
| Or down to SL | Bid 2644.90 | Entry closes → EA closes hedge on the next tick |

| Path (equal lots, 5-pip spread) | No hedge | With hedge |
|---|---|---|
| Straight down, never armed | −51 | −51 (never hedged) |
| Armed, then down to SL | −51 | ≈ −6 + commissions |
| Up to +20, then back down | ≈ 0 | ≈ −22 |
| Up to TP (+200) | +200 | ≈ +178 |

## Warnings and limitations

- **Never armed = never hedged:** a trade that goes straight against you takes its full SL.
- **Hedge break-even gap:** if `InpHedgeBEPips` closes a hedge near its open price, the entry stays unhedged until price trades back beyond the arm level; a renewed drop can reach the full entry SL. Use `InpHedgeBEPips = 0` to keep the hedge until the entry reaches break-even or closes.
- **Backstop buffer:** `InpHedgeSLBufferPips` must exceed the widest expected spread; at 0 the backstop SL (hit by Ask) fires one spread before the entry's break-even (hit by Bid).
- **Costs:** every hedge adds a spread and a commission, plus swap on both legs overnight. A choppy market that arms and triggers repeatedly stacks these costs.
- **Margin:** brokers that charge full margin on hedged positions can reject large hedges; failures are logged and retried every `HEDGE_RETRY_SEC`.
- **Multiplier > 1.0** flips net exposure to the hedge side (hard cap 1.5).
- **Comment link:** if a broker rewrites position comments, a hedge can no longer be matched to its entry; it is then left to its own SL/TP. Verify on demo.
- **Netting accounts:** an opposite order closes the entry — `InitHedge()` refuses to run there.
