# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

