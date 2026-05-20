# Roadmap

## Completed in v2.0.0

- ✅ Canonical reusable snippets: risk engine, filters, position management, logging.
- ✅ Strategy-specific prompt packs: CRT, SMC, ICT, Asian Range, Grid, Indicator.
- ✅ Structured scoring checklist for AI-generated `.mq5` output (Section 13 + blueprint).
- ✅ Expanded eval cases for common MQL5 patterns.

## Near Term

- Add CI workflow (GitHub Actions) to run `validate_repo.py` on every pull request.
- Add sample generated EAs (complete `.mq5` files) demonstrating safe implementation.
- Add MetaEditor compile error reference guide (common errors + fixes).

## Mid Term

- Add Telegram bot integration example (WebRequest pattern).
- Add news filter implementation using MT5 Economic Calendar.
- Add portfolio EA example (multi-symbol, correlated position sizing).
- Add multilingual setup docs (Bahasa Indonesia, Spanish, Chinese).

## Long Term

- Build automated static analysis for generated MQL5 code (Python AST-style parser).
- Add strategy-specific eval packs with expected backtest metric ranges.
- Add community-contributed prompt packs (breakout, mean-reversion, scalping).
