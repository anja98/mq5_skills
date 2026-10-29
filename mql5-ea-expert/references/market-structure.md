# Structural HH/HL and LL/LH — Complete Module (MQL5)

Reference for **Section 6.2.1** of `SKILL.md`. Read this before implementing structural Higher High / Higher Low (bullish) or Lower Low / Lower High (bearish) detection, BOS, CHoCH or inducement (IDM) sweeps.

---

## 1. Rules (one code path for both directions)

The engine tracks one active direction `d` (`+1` bullish, `-1` bearish) and uses four helpers. There is no duplicated bearish copy.

| Helper | Bullish (`d=+1`) | Bearish (`d=-1`) |
|---|---|---|
| `Lead(d, bar)` | High | Low |
| `Trail(d, bar)` | Low | High |
| `Beyond(d, a, b)` | `a > b` | `a < b` |
| `Behind(d, a, b)` | `a < b` | `a > b` |

| Term | Bullish | Bearish |
|---|---|---|
| **Anchor** | Structural low | Structural high |
| **Leg extreme** | Highest High of the current leg | Lowest Low of the current leg |
| **IDM (inducement)** | Latest confirmed swing **low** after the anchor, above it, before the leg extreme | Latest confirmed swing **high** after the anchor, below it, before the leg extreme |
| **IDM sweep** | Low trades below IDM (or close, if `SWEEP_CLOSE`) | High trades above IDM (or close) |
| **Valid extreme** | **HH** (leg extreme at the moment of the sweep) | **LL** |
| **BOS** | Close above HH (or wick, if `BOS_WICK`) | Close below LL (or wick) |
| **Valid retracement** | **HL**: lowest Low from the HH bar to the BOS bar, must be above the anchor | **LH**: highest High from the LL bar to the BOS bar, must be below the anchor |
| **Structure break (CHoCH)** | Close below the anchor | Close above the anchor |

Swings (fractals) are N bars strictly higher/lower on each side, confirmed N bars late, and are used **only for IDM selection and bootstrap**. The leg extreme is bar-level, so no lag-compensation re-scan is needed. A sweep inside the N-bar confirmation window is detected on its own bar. A swing can never be the IDM before it is confirmed, but a sweep of a swing low is impossible inside its own confirmation window, so nothing is missed.

### State machine (per closed bar, in this order)

1. **Swing update:** confirm the pivot N bars back (high and/or low).
2. **No trend yet:** bootstrap (section 2) and stop.
3. **Structure break:** if the bar closes `Behind` the anchor, emit `STRUCTURE_BROKEN`, flip direction (section 3) and stop.
4. **Phase SEEK:** update the leg extreme if the bar goes `Beyond` it. If the bar is after the extreme, the extreme is `Beyond` the last broken level, and an IDM exists, check the sweep. On a sweep, emit `IDM_SWEEP` and `EXTREME_CONFIRMED` (HH or LL), go to AWAIT_BOS.
5. **Phase AWAIT_BOS:** if BOS, emit `BOS`, compute the retracement extreme from the HH/LL bar to now. If it is `Beyond` the anchor, emit `RETRACE_CONFIRMED` (HL or LH) and make it the new anchor. Otherwise emit `RETRACE_REJECTED` (wick undercut) and keep the anchor. Either way the broken level becomes the HH/LL, the leg extreme restarts from the highest/lowest point since the new anchor, go to SEEK.

Without an IDM sweep nothing is labelled, even if price keeps making higher highs.

---

## 2. Bootstrap

State starts at `NONE`. With at least one confirmed swing high `SH` (most recent) and one confirmed swing low `SL` (most recent) and `SL < SH`:

- **Bull start:** a bar closes above `SH`. Anchor = `SL`, broken level = `SH`.
- **Bear start:** a bar closes below `SL`. Anchor = `SH`, broken level = `SL`.

The leg extreme starts as the most extreme bar from the anchor to the current bar. Emit `TREND_START`.

## 3. Flip on structure break (CHoCH)

When a bar closes `Behind` the anchor of direction `d`:

- Emit `STRUCTURE_BROKEN` (point = old anchor).
- **New anchor = highest high of the failed leg** (bullish failing) or lowest low (bearish failing): the most extreme price from the old anchor bar through the breaking bar.
- Broken level = the old anchor. New leg extreme = the most extreme bar in the new direction from the new anchor bar through the breaking bar.
- Emit `TREND_START` (new direction, note `CHOCH`).

`CHoCHOnLastBar(dir)` returns true only for a flip, not for the first bootstrap.

---

## 4. Module: `Include/ProjectName/MarketStructure.mqh`

```mql5
//+------------------------------------------------------------------+
//| MarketStructure.mqh                                              |
//| Project: [ProjectName] v1.00                                     |
//| Author:  [Author]                                                |
//| Purpose: Structural HH/HL (bull) and LL/LH (bear) engine with    |
//|          IDM sweep, BOS and CHoCH flip. Closed bars only.        |
//| Build:   MT5 2450+  |  Updated: 2026-10-29                      |
//+------------------------------------------------------------------+
#property copyright "[Author]"
#property link      "[URL or contact]"
#property version   "1.00"
#property strict

#define MS_BULL      1
#define MS_BEAR     -1
#define MS_BUF_CAP   8192     // bar ring buffer (bars kept for scans)
#define MS_SW_CAP    256      // swings kept per side
#define MS_EV_CAP    4096     // event queue capacity (drain after Rebuild)

enum ENUM_MS_BOS_MODE   { MS_BOS_CLOSE = 0, MS_BOS_WICK = 1 };
enum ENUM_MS_SWEEP_MODE { MS_SWEEP_WICK = 0, MS_SWEEP_CLOSE = 1 };

enum ENUM_MS_EVENT
{
   MS_TREND_START = 0,      // bootstrap or CHoCH flip (note says which)
   MS_IDM_SWEEP,            // point = the inducement level that was swept
   MS_EXTREME_CONFIRMED,    // HH (dir +1) or LL (dir -1)
   MS_BOS,                  // point = the HH/LL level that was broken
   MS_RETRACE_CONFIRMED,    // HL (dir +1) or LH (dir -1)
   MS_RETRACE_REJECTED,     // retracement undercut the anchor (wick)
   MS_STRUCTURE_BROKEN      // close beyond the anchor; point = old anchor
};

struct SMSPoint
{
   datetime time;
   double   price;
   int      seq;            // internal bar sequence number, -1 = invalid
};

struct SMSEvent
{
   ENUM_MS_EVENT type;
   int           dir;       // +1 bullish context, -1 bearish context
   datetime      bar_time;  // bar on which the event was detected
   SMSPoint      point;
   string        note;
};

void MSSetPoint(SMSPoint &p, const datetime t, const double price, const int seq)
{
   p.time = t; p.price = price; p.seq = seq;
}
void MSResetPoint(SMSPoint &p) { p.time = 0; p.price = 0.0; p.seq = -1; }
bool MSValid(const SMSPoint &p) { return (p.seq >= 0); }

string MSEventLabel(const SMSEvent &e)
{
   switch(e.type)
   {
      case MS_TREND_START:       return (e.dir > 0) ? "BULL START"  : "BEAR START";
      case MS_IDM_SWEEP:         return "IDM SWEEP";
      case MS_EXTREME_CONFIRMED: return (e.dir > 0) ? "HH" : "LL";
      case MS_BOS:               return (e.dir > 0) ? "BOS UP" : "BOS DOWN";
      case MS_RETRACE_CONFIRMED: return (e.dir > 0) ? "HL" : "LH";
      case MS_RETRACE_REJECTED:  return (e.dir > 0) ? "HL REJECTED" : "LH REJECTED";
      case MS_STRUCTURE_BROKEN:  return (e.dir > 0) ? "BULL BROKEN" : "BEAR BROKEN";
   }
   return "?";
}

//+------------------------------------------------------------------+
//| Chronological swing list (oldest first), bounded                 |
//+------------------------------------------------------------------+
class CSwingList
{
private:
   SMSPoint m_pt[];
   int      m_count;
public:
   CSwingList() : m_count(0) { ArrayResize(m_pt, MS_SW_CAP); }
   void Reset()       { m_count = 0; }
   int  Count() const { return m_count; }

   void Add(const SMSPoint &p)
   {
      if(m_count >= MS_SW_CAP)
      {
         for(int i = 1; i < m_count; i++) m_pt[i - 1] = m_pt[i];
         m_count--;
      }
      m_pt[m_count] = p;
      m_count++;
   }

   bool At(const int idx, SMSPoint &out) const
   {
      if(idx < 0 || idx >= m_count) return false;
      out = m_pt[idx];
      return true;
   }
};

//+------------------------------------------------------------------+
//| CMarketStructure                                                 |
//+------------------------------------------------------------------+
class CMarketStructure
{
private:
   // configuration
   string             m_symbol;
   ENUM_TIMEFRAMES    m_tf;
   int                m_lookback;
   int                m_history;
   ENUM_MS_BOS_MODE   m_bosMode;
   ENUM_MS_SWEEP_MODE m_sweepMode;
   bool               m_ready;

   // closed-bar ring buffer
   MqlRates           m_buf[];
   int                m_seq;        // sequence number of the newest bar, -1 = none
   datetime           m_lastTime;

   // swings
   CSwingList         m_hi;
   CSwingList         m_lo;

   // structure state
   int                m_dir;        // +1 / -1 / 0 (none)
   int                m_phase;      // 0 = SEEK (extreme + sweep), 1 = AWAIT_BOS
   SMSPoint           m_anchor;     // structural low (bull) / structural high (bear)
   SMSPoint           m_broken;     // last broken structural extreme
   SMSPoint           m_legExt;     // running extreme of the current leg
   SMSPoint           m_ext;        // confirmed HH / LL awaiting BOS
   SMSPoint           m_lastExt;    // last confirmed HH / LL (for getters)
   SMSPoint           m_lastRet;    // last confirmed HL / LH (for getters)
   int                m_flipDir;
   int                m_flipSeq;

   // event ring queue
   SMSEvent           m_ev[];
   int                m_evHead;
   int                m_evCount;

   //--- direction helpers -------------------------------------------
   bool   Beyond(const int d, const double a, const double b) const { return (d > 0) ? (a > b) : (a < b); }
   bool   Behind(const int d, const double a, const double b) const { return (d > 0) ? (a < b) : (a > b); }
   double Lead(const int d, const MqlRates &r)  const { return (d > 0) ? r.high : r.low; }
   double Trail(const int d, const MqlRates &r) const { return (d > 0) ? r.low  : r.high; }

   bool BarAt(const int seq, MqlRates &r) const
   {
      if(seq < 0 || seq > m_seq || seq <= m_seq - MS_BUF_CAP) return false;
      r = m_buf[seq % MS_BUF_CAP];
      return true;
   }

   void Push(const ENUM_MS_EVENT type, const int d, const datetime barTime,
             const SMSPoint &p, const string note)
   {
      SMSEvent e;
      e.type = type; e.dir = d; e.bar_time = barTime; e.point = p; e.note = note;
      if(m_evCount >= MS_EV_CAP)
      {
         m_evHead = (m_evHead + 1) % MS_EV_CAP;
         m_evCount--;
      }
      m_ev[(m_evHead + m_evCount) % MS_EV_CAP] = e;
      m_evCount++;
   }

   // Most extreme bar in [fromSeq..toSeq]. leading=true: Lead side (HH/LL),
   // leading=false: Trail side (HL/LH). Earliest bar wins ties (strict compare).
   bool ScanBars(const int fromSeq, const int toSeq, const int d,
                 const bool leading, SMSPoint &out)
   {
      int start = MathMax(fromSeq, MathMax(0, m_seq - MS_BUF_CAP + 1));
      bool found = false;
      for(int s = start; s <= toSeq; s++)
      {
         MqlRates r;
         if(!BarAt(s, r)) continue;
         double v = leading ? Lead(d, r) : Trail(d, r);
         bool better = !found;
         if(found) better = leading ? Beyond(d, v, out.price) : Behind(d, v, out.price);
         if(better) { MSSetPoint(out, r.time, v, s); found = true; }
      }
      return found;
   }

   void DetectSwings()
   {
      int p = m_seq - m_lookback;
      if(p < m_lookback) return;
      MqlRates c;
      if(!BarAt(p, c)) return;
      bool isHigh = true, isLow = true;
      for(int k = 1; k <= m_lookback; k++)
      {
         MqlRates l, r;
         if(!BarAt(p - k, l) || !BarAt(p + k, r)) return;
         if(!(c.high > l.high && c.high > r.high)) isHigh = false;
         if(!(c.low  < l.low  && c.low  < r.low))  isLow  = false;
         if(!isHigh && !isLow) return;
      }
      SMSPoint pt;
      if(isHigh) { MSSetPoint(pt, c.time, c.high, p); m_hi.Add(pt); }
      if(isLow)  { MSSetPoint(pt, c.time, c.low,  p); m_lo.Add(pt); }
   }

   // IDM = latest confirmed retracement-side swing strictly between the anchor
   // and the leg extreme (in time), on the trend side of the anchor (in price).
   bool FindIdm(const int d, SMSPoint &out)
   {
      CSwingList *lst = (d > 0) ? GetPointer(m_lo) : GetPointer(m_hi);
      for(int i = lst.Count() - 1; i >= 0; i--)
      {
         SMSPoint p;
         if(!lst.At(i, p)) continue;
         if(p.seq >= m_legExt.seq) continue;
         if(p.seq <= m_anchor.seq) break;
         if(!Beyond(d, p.price, m_anchor.price)) continue;
         out = p;
         return true;
      }
      return false;
   }

   void Bootstrap(const int s, const MqlRates &b)
   {
      if(m_hi.Count() == 0 || m_lo.Count() == 0) return;
      SMSPoint sh, sl;
      if(!m_hi.At(m_hi.Count() - 1, sh)) return;
      if(!m_lo.At(m_lo.Count() - 1, sl)) return;
      int d = 0;
      if(b.close > sh.price && sl.price < sh.price)      d = MS_BULL;
      else if(b.close < sl.price && sh.price > sl.price) d = MS_BEAR;
      if(d == 0) return;
      m_dir = d;
      m_phase = 0;
      if(d > 0) { m_anchor = sl; m_broken = sh; }
      else      { m_anchor = sh; m_broken = sl; }
      if(!ScanBars(m_anchor.seq, s, d, true, m_legExt))
         MSSetPoint(m_legExt, b.time, Lead(d, b), s);
      Push(MS_TREND_START, d, b.time, m_anchor, "BOOTSTRAP");
   }

   void Flip(const int s, const MqlRates &b)
   {
      const int d  = m_dir;
      const int nd = -d;
      Push(MS_STRUCTURE_BROKEN, d, b.time, m_anchor, "");
      SMSPoint pk;
      if(!ScanBars(m_anchor.seq, s, d, true, pk))
         MSSetPoint(pk, b.time, Lead(d, b), s);
      m_broken = m_anchor;
      m_anchor = pk;
      m_dir = nd;
      m_phase = 0;
      if(!ScanBars(pk.seq, s, nd, true, m_legExt))
         MSSetPoint(m_legExt, b.time, Lead(nd, b), s);
      MSResetPoint(m_ext);
      MSResetPoint(m_lastExt);
      MSResetPoint(m_lastRet);
      m_flipDir = nd;
      m_flipSeq = s;
      Push(MS_TREND_START, nd, b.time, m_anchor, "CHOCH");
   }

   void SeekSweep(const int s, const MqlRates &b, const int d)
   {
      if(Beyond(d, Lead(d, b), m_legExt.price))
         MSSetPoint(m_legExt, b.time, Lead(d, b), s);
      if(s <= m_legExt.seq) return;                          // extreme must precede the sweep bar
      if(!Beyond(d, m_legExt.price, m_broken.price)) return; // must exceed the last broken level
      SMSPoint idm;
      if(!FindIdm(d, idm)) return;
      double px = (m_sweepMode == MS_SWEEP_WICK) ? Trail(d, b) : b.close;
      if(!Behind(d, px, idm.price)) return;
      m_ext = m_legExt;
      m_lastExt = m_ext;
      m_phase = 1;
      Push(MS_IDM_SWEEP, d, b.time, idm, "");
      Push(MS_EXTREME_CONFIRMED, d, b.time, m_ext, "");
   }

   void AwaitBos(const int s, const MqlRates &b, const int d)
   {
      double px = (m_bosMode == MS_BOS_CLOSE) ? b.close : Lead(d, b);
      if(!Beyond(d, px, m_ext.price)) return;
      SMSPoint ret;
      if(!ScanBars(m_ext.seq, s, d, false, ret)) return;
      Push(MS_BOS, d, b.time, m_ext, "");
      int legFrom = m_ext.seq;
      if(Beyond(d, ret.price, m_anchor.price))
      {
         Push(MS_RETRACE_CONFIRMED, d, b.time, ret, "");
         m_anchor  = ret;
         m_lastRet = ret;
         legFrom   = ret.seq;
      }
      else
      {
         Push(MS_RETRACE_REJECTED, d, b.time, ret, "BEYOND_ANCHOR");
      }
      m_broken = m_ext;
      if(!ScanBars(legFrom, s, d, true, m_legExt))
         MSSetPoint(m_legExt, b.time, Lead(d, b), s);
      m_phase = 0;
   }

   void ProcessBar(const int s, const MqlRates &b)
   {
      if(m_dir == 0) { Bootstrap(s, b); return; }
      const int d = m_dir;
      if(Behind(d, b.close, m_anchor.price)) { Flip(s, b); return; }
      if(m_phase == 0) SeekSweep(s, b, d);
      else             AwaitBos(s, b, d);
   }

   void Reset()
   {
      m_seq = -1; m_lastTime = 0;
      m_hi.Reset(); m_lo.Reset();
      m_dir = 0; m_phase = 0;
      MSResetPoint(m_anchor); MSResetPoint(m_broken); MSResetPoint(m_legExt);
      MSResetPoint(m_ext);    MSResetPoint(m_lastExt); MSResetPoint(m_lastRet);
      m_flipDir = 0; m_flipSeq = -1;
      m_evHead = 0; m_evCount = 0;
   }

public:
   CMarketStructure() : m_ready(false), m_seq(-1), m_lastTime(0), m_dir(0), m_phase(0),
                        m_flipDir(0), m_flipSeq(-1), m_evHead(0), m_evCount(0) {}

   bool Init(const string symbol, const ENUM_TIMEFRAMES tf, const int lookback,
             const ENUM_MS_BOS_MODE bos, const ENUM_MS_SWEEP_MODE sweep,
             const int historyBars)
   {
      if(lookback < 1 || lookback > 50)       { Print("[ERROR] MS lookback must be 1..50"); return false; }
      if(historyBars < 2 * lookback + 10)     { Print("[ERROR] MS history too small");      return false; }
      m_symbol    = symbol;
      m_tf        = (tf == PERIOD_CURRENT) ? (ENUM_TIMEFRAMES)_Period : tf;
      m_lookback  = lookback;
      m_history   = MathMin(historyBars, MS_BUF_CAP);
      m_bosMode   = bos;
      m_sweepMode = sweep;
      ArrayResize(m_buf, MS_BUF_CAP);
      ArrayResize(m_ev,  MS_EV_CAP);
      Reset();
      m_ready = true;
      return true;
   }

   // Feed one CLOSED bar (strictly increasing time). Used directly by tests.
   bool AddBar(const MqlRates &r)
   {
      if(!m_ready) return false;
      if(m_seq >= 0 && r.time <= m_lastTime) return false;
      m_seq++;
      m_buf[m_seq % MS_BUF_CAP] = r;
      m_lastTime = r.time;
      DetectSwings();
      ProcessBar(m_seq, r);
      return true;
   }

   // Replay the last m_history closed bars. Drain events afterwards.
   bool Rebuild()
   {
      if(!m_ready) return false;
      Reset();
      MqlRates rates[];
      ArraySetAsSeries(rates, false);                 // index 0 = oldest
      int got = CopyRates(m_symbol, m_tf, 1, m_history, rates);   // start 1 = skip forming bar
      if(got <= 0) { Print("[WARN] MS Rebuild: CopyRates failed, err=", GetLastError()); return false; }
      for(int i = 0; i < got; i++) AddBar(rates[i]);
      return true;
   }

   // Process every closed bar not yet seen. Returns number of bars processed.
   int Update()
   {
      if(!m_ready) return 0;
      if(m_seq < 0) return Rebuild() ? (m_seq + 1) : 0;
      datetime lastClosed = iTime(m_symbol, m_tf, 1);
      if(lastClosed == 0 || lastClosed <= m_lastTime) return 0;
      MqlRates tmp[];
      ArraySetAsSeries(tmp, false);
      int n = CopyRates(m_symbol, m_tf, m_lastTime + 1, lastClosed, tmp);
      if(n <= 0) return 0;
      int done = 0;
      for(int i = 0; i < n; i++) if(AddBar(tmp[i])) done++;
      return done;
   }

   bool PopEvent(SMSEvent &e)
   {
      if(m_evCount <= 0) return false;
      e = m_ev[m_evHead];
      m_evHead = (m_evHead + 1) % MS_EV_CAP;
      m_evCount--;
      return true;
   }

   int  Trend()      const { return m_dir; }       // +1 bull, -1 bear, 0 none
   int  Phase()      const { return m_phase; }     // 0 = seeking sweep, 1 = awaiting BOS
   bool CHoCHOnLastBar(const int dir) const { return (m_seq >= 0 && m_flipSeq == m_seq && m_flipDir == dir); }
   datetime LastBarTime() const { return m_lastTime; }

   bool GetAnchor(SMSPoint &p)      const { if(m_dir == 0) return false; p = m_anchor; return true; }
   bool GetBrokenLevel(SMSPoint &p) const { if(m_dir == 0) return false; p = m_broken; return true; }
   bool GetLastExtreme(SMSPoint &p) const { if(!MSValid(m_lastExt)) return false; p = m_lastExt; return true; }  // last HH / LL
   bool GetLastRetrace(SMSPoint &p) const { if(!MSValid(m_lastRet)) return false; p = m_lastRet; return true; }  // last HL / LH
};

//+------------------------------------------------------------------+
//| Chart drawing (optional)                                         |
//+------------------------------------------------------------------+
class CMSChart
{
private:
   string m_prefix;
   long   m_chart;
   int    m_n;

   color Col(const int d) const { return (d > 0) ? clrDodgerBlue : clrTomato; }

   void Text(const datetime t, const double price, const string txt,
             const color c, const bool above)
   {
      string name = m_prefix + IntegerToString(m_n++);
      if(!ObjectCreate(m_chart, name, OBJ_TEXT, 0, t, price)) return;
      ObjectSetString(m_chart,  name, OBJPROP_TEXT, txt);
      ObjectSetInteger(m_chart, name, OBJPROP_COLOR, c);
      ObjectSetInteger(m_chart, name, OBJPROP_FONTSIZE, 9);
      ObjectSetInteger(m_chart, name, OBJPROP_ANCHOR, above ? ANCHOR_LOWER : ANCHOR_UPPER);
   }

   void Line(const datetime t1, const datetime t2, const double price,
             const color c, const ENUM_LINE_STYLE style)
   {
      string name = m_prefix + IntegerToString(m_n++);
      if(!ObjectCreate(m_chart, name, OBJ_TREND, 0, t1, price, t2, price)) return;
      ObjectSetInteger(m_chart, name, OBJPROP_COLOR, c);
      ObjectSetInteger(m_chart, name, OBJPROP_STYLE, style);
      ObjectSetInteger(m_chart, name, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(m_chart, name, OBJPROP_SELECTABLE, false);
   }

public:
   CMSChart() : m_prefix("MS_"), m_chart(0), m_n(0) {}

   void Init(const string prefix, const long chartId = 0)
   {
      m_prefix = prefix; m_chart = chartId; m_n = 0;
   }

   void Draw(const SMSEvent &e)
   {
      if(MQLInfoInteger(MQL_TESTER) && !MQLInfoInteger(MQL_VISUAL_MODE)) return;
      const color c = Col(e.dir);
      switch(e.type)
      {
         case MS_EXTREME_CONFIRMED:
            Text(e.point.time, e.point.price, (e.dir > 0) ? "HH" : "LL", c, (e.dir > 0));
            break;
         case MS_RETRACE_CONFIRMED:
            Text(e.point.time, e.point.price, (e.dir > 0) ? "HL" : "LH", c, (e.dir < 0));
            break;
         case MS_IDM_SWEEP:
            Line(e.point.time, e.bar_time, e.point.price, c, STYLE_DOT);
            Text(e.point.time, e.point.price, "IDM", c, (e.dir < 0));
            break;
         case MS_BOS:
            Line(e.point.time, e.bar_time, e.point.price, c, STYLE_SOLID);
            Text(e.bar_time, e.point.price, "BOS", c, (e.dir > 0));
            break;
         case MS_STRUCTURE_BROKEN:
            Text(e.bar_time, e.point.price, "CHoCH", c, (e.dir < 0));
            break;
         default:
            break;
      }
   }

   void Clear() { ObjectsDeleteAll(m_chart, m_prefix); m_n = 0; }
};
```

---

## 5. EA wiring

```mql5
#include <ProjectName/MarketStructure.mqh>

input group "=== MARKET STRUCTURE ==="
input int                InpMSSwingLookback = 3;                // swing N bars each side (1..50)
input ENUM_MS_BOS_MODE   InpMSBosMode       = MS_BOS_CLOSE;
input ENUM_MS_SWEEP_MODE InpMSSweepMode     = MS_SWEEP_WICK;
input int                InpMSHistoryBars   = 2000;
input bool               InpMSDraw          = true;

CMarketStructure c_MS;
CMSChart         c_MSChart;

void DrainStructureEvents()
{
   SMSEvent e;
   while(c_MS.PopEvent(e))
   {
      if(InpMSDraw) c_MSChart.Draw(e);
      Print("[STRUCT] ", MSEventLabel(e), " @", DoubleToString(e.point.price, _Digits),
            " bar=", TimeToString(e.bar_time), " ", e.note);
   }
}

int OnInit()
{
   if(!c_MS.Init(_Symbol, PERIOD_CURRENT, InpMSSwingLookback,
                 InpMSBosMode, InpMSSweepMode, InpMSHistoryBars))
      return INIT_PARAMETERS_INCORRECT;
   if(InpMSDraw) c_MSChart.Init("MS_");
   c_MS.Rebuild();
   DrainStructureEvents();
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { c_MSChart.Clear(); }

void OnTick()
{
   if(IsNewBar())                 // Section 5.2
   {
      c_MS.Update();              // processes closed bars only
      DrainStructureEvents();
   }
   // Consumers (read-only):
   //   c_MS.Trend()                 +1 / -1 / 0
   //   c_MS.GetAnchor(p)            latest structural low (bull) / high (bear), e.g. stop-loss reference
   //   c_MS.GetLastExtreme(p)       last confirmed HH / LL
   //   c_MS.GetLastRetrace(p)       last confirmed HL / LH
   //   c_MS.CHoCHOnLastBar(+1)      bullish CHoCH on the bar that just closed
}
```

The engine never trades and never reads bar shift 0. `Update()` copes with gaps by processing every closed bar since the last one it saw.

---

## 6. Integration rules

- Create the engine in `OnInit`, call `Rebuild()` once, then `Update()` **only on a new bar**. Drain events after both calls (`MS_EV_CAP` is 4096; draining after `Rebuild()` matters on long histories).
- Feed **closed bars only**. Never mix shift 0 into the structure logic.
- Use the engine's own getters for stops/targets (for example `GetAnchor()`), not a second hand-rolled swing search.
- `DetectCHoCH()` in Section 6.2 delegates to `CHoCHOnLastBar()`.
- Strategy Tester and live runs must produce identical events. Compare an `Update()`-driven run with a fresh `Rebuild()` on the same history when validating.
- The module places no orders. Entry/exit logic and risk management stay in the existing engines.

## 7. Warnings

- **Labelling tool, not an edge.** Valid HH/HL/LL/LH, BOS and CHoCH are a way to read structure. They say nothing about profitability. Backtest any rule built on them.
- **Source ambiguity.** The ICT/SMC literature is loose on inducement selection, tie-breaking and CHoCH anchors. The choices here (latest IDM, wick sweep, close BOS, highest high of the failed leg as the flip anchor) are defaults to tune, not truths.
- **Late flips.** Structure breaks need a bar **close** beyond the anchor, so a flip is detected only after that close. Wicks alone never flip the trend.
- **Rejected HL.** `RETRACE_REJECTED` means the retracement wicked beyond the anchor without closing beyond it. The anchor is kept. Decide explicitly how your EA treats that state.
- **Buffer limits.** Scans are clamped to the last 8192 bars (`MS_BUF_CAP`). A single leg longer than that is truncated. Anchors are normally far closer.
- **Equal highs/lows** are not swings (strict comparison), so flat tops can delay the IDM.
- **Bootstrap is simplified.** It uses the most recent confirmed swings, not a full CHoCH history. Expect the first few labels after attaching to differ from a chart marked by hand from further back, until the engine has seen a few legs.
- **Drawing** is skipped in non-visual tester runs. Do not rely on chart objects for logic.
