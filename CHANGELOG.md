# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-20

### Added
- 16-section structured skill replacing the original 4-section layout.
- 12 canonical MQL5 patterns: handle lifecycle, risk calc, BE, trailing, partial close, pre-flight check, etc.
- Strategy frameworks: CRT, SMC (BOS/FVG/OB), ICT (kill zones, Silver Bullet), Asian Range, MTF confluence.
- Production-grade prop firm safety module (FTMO, The5%ers, E8 compatible).
- `CDashboard` OOP class for CChartObject panels.
- `CTradeLogger` OOP class for CSV trade journal.
- Custom `OnTester()` composite metric for Strategy Tester optimization.
- 8 new ready-to-use example prompts (CRT, SMC OB+FVG, ICT Silver Bullet, Asian Range, Safe Grid, Custom Indicator).
- Expanded pitfall table from 9 to 14 items with wrong/correct comparisons.
- Pre-code requirements checklist expanded to 28 questions.

### Changed
- SKILL.md version 1.2.0 → 2.0.0.
- evals.json version 1.2.0 → 2.0.0.
- `templates/ea-blueprint.md` rewritten with full section ordering, naming table, multi-file layout.
- README updated to reflect v2.0.0 improvements.

### Removed
- `docs/reports/COMPLETION_REPORT.md` — internal development note, not user-facing.
- `docs/reports/FIX_SUMMARY.md` — internal fix notes, not user-facing.
- `docs/GITHUB_DESCRIPTIONS.md` — meta marketing copy, not skill content.
- `docs/UPLOAD_GUIDE.md` — content consolidated into `docs/AI_SETUP_GUIDE.md`.

## [1.2.0] - 2026-05-20

### Added
- Structured repository layout: `docs/`, `examples/`, `templates/`, `tools/`.
- Reusable EA generation blueprint in `templates/ea-blueprint.md`.
- Copy-paste prompt library in `examples/prompts/README.md`.
- Lightweight validation script: `tools/validate_repo.py`.
- Project roadmap and contribution guide.

### Changed
- README now reflects current project structure and validation workflow.
- Operational reports moved under `docs/reports/`.

## [1.1.0] - 2026-02-12

### Fixed - Critical Compile Errors
- **[CRITICAL]** Fixed `CollectFeatures()` incorrect return type - now uses pass-by-reference
- **[CRITICAL]** Fixed all indicator functions (iMA, iRSI, iATR, iBands) - now properly use handles + CopyBuffer
- **[CRITICAL]** Fixed `CTrade::PositionModify` signature - use symbol instead of ticket
- **[CRITICAL]** Fixed `CTrade::PositionClose` signature - use symbol instead of ticket
- **[CRITICAL]** Fixed pointer usage in examples - changed `.` to `->`

### Fixed - Major Logic Bugs
- **[MAJOR]** Fixed `GetAdjustedRiskPercent()` condition ordering bug (>= 5 before >= 3)
- **[MAJOR]** Fixed `CheckTradeSignals()` - now filters by MagicNumber
- **[MAJOR]** Fixed Martingale `CanTrade()` contradiction - sets m_isActive=false on loss
- **[MAJOR]** Fixed `CBacktestValidator` initial balance - captured at construction
- **[MAJOR]** Fixed Sharpe Ratio deal filtering - now filters DEAL_ENTRY_OUT
- **[MAJOR]** Fixed `CalculateStats()` deal filtering - now uses DEAL_ENTRY instead of DEAL_TYPE
- Fixed ORDER_FILLING_FOK hardcoded - now uses SetTypeFillingBySymbol()
- Fixed memory leaks in usage examples - added delete in OnDeinit()
- Fixed `CollectFeatures[9]` missing assignment - reduced array to 9 elements
- Fixed division by zero guards in CollectFeatures

### Added - Documentation & Structure
- AI Response Contract section with output requirements and safety rules
- Table of Contents for better navigation (9 major sections)
- Frontmatter with version, language, license, tags, scope_limits
- .gitignore file for MetaEditor/IDE/OS files
- CHANGELOG.md (this file)
- FIX_SUMMARY.md - Technical review report

### Changed - Language & Professional Polish
- Converted all Indonesian text to English for universal compatibility
- Rewrote README.md - concise, professional, accurate structure
- Improved evals.json with measurable assertions (9 tests including adversarial)
- Updated frontmatter: version 1.0.0 → 1.1.0
- Improved code quality to compile-ready production standard

### Improved - Evaluations
- Added measurable expectations (required classes, functions, parameters)
- Converted prompts to English
- Added adversarial test case (refuse unsafe feature removal)
- Structured expectations as JSON objects for machine validation
- Added 9th eval test for safety rule enforcement

## [1.0.0] - 2026-01-01

### Added
- Initial release
- Professional EA template
- Multi-Timeframe Analysis class
- Advanced Money Management class
- Safe Grid System class
- Ultra-Safe Martingale class
- Backtest Validator class
- 8 evaluation test cases
- Comprehensive documentation

