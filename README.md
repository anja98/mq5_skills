# MQL5 EA Expert - Professional AI Skill

> **Version 2.0.0** | Universal AI skill for creating production-ready MetaTrader 5 Expert Advisors with a survival-first approach.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MQL5](https://img.shields.io/badge/MQL5-Expert_Advisor-blue.svg)](https://www.mql5.com)

---

## 🎯 What is This?

An AI skill that teaches Claude, ChatGPT, Gemini, and other AI assistants how to generate **compile-ready**, professional MQL5 Expert Advisors with emphasis on **capital preservation** over maximum returns.

### Key Differentiators
- ✅ **Compile-Ready Code** - All templates verified in MetaEditor
- ✅ **Production-Grade** - Real-world risk management, not backtest fantasies
- ✅ **Universal** - Works with any AI that processes Markdown
- ✅ **Safety-First** - Mandatory risk controls, warnings for dangerous strategies

---

## 🚀 Quick Start

### Via skills CLI (Recommended)
```bash
npx skills add nawf-dev/mq5_skills
```

### For Claude (Anthropic)
```bash
# Upload mql5-ea-expert/SKILL.md to your Claude skills directory
# Claude auto-applies it when generating EAs
```

### For ChatGPT (OpenAI)
1. Create Custom GPT
2. Upload `mql5-ea-expert/SKILL.md` to Knowledge Base
3. System instructions: "Follow MQL5 EA Expert skill guidelines"

### For Other AI
- Upload `mql5-ea-expert/SKILL.md` into conversation context
- Or paste relevant sections when needed

**Test it:**
```
Create an RSI strategy EA with:
- RSI period 14, overbought 70, oversold 30
- 1% risk per trade
- Daily loss limit 5%
```

Expected: Compile-ready `.mq5` file with proper risk management ✅

---

## 📁 Repository Structure

```
mq5_sklis/
├── mql5-ea-expert/           # Skill package (skills.sh compatible)
│   ├── SKILL.md              #   Core AI skill — load this into your AI
│   └── references/
│       ├── ea-blueprint.md   #   EA output blueprint & standards
│       └── example-prompts.md#   8 ready-to-use prompts
├── evals.json                # Skill validation test cases
├── README.md                 # Project overview
├── CHANGELOG.md              # Version history
├── LICENSE                   # MIT + trading disclaimer
├── docs/
│   ├── AI_SETUP_GUIDE.md     # Setup for Claude / ChatGPT / Gemini
│   └── ROADMAP.md            # Planned improvements
└── tools/
    └── validate_repo.py      # Repo structure validator
```

**Install via skills CLI:**
```bash
npx skills add YOUR_GITHUB_USERNAME/mq5_sklis
```

---

## 💡 What You Get

### Core Templates
- **Professional EA Structure** - Organized inputs, error handling, logging
- **Multi-Timeframe Analysis** - Trend confirmation across H4/H1/M15
- **Money Management** - Fixed risk, Kelly Criterion, adaptive risk
- **Safe Grid System** - Grid trading with drawdown caps
- **Ultra-Safe Martingale** - Martingale with forced safety limits

### Safety Built-In
- Automatic risk per trade <= 1%
- Daily loss limit <= 5%
- Max drawdown protection <= 20%
- Spread filters, time filters, margin checks
- Magic number position tracking

### AI Response Contract
The skill instructs AI to:
1. **Always** restate requirements before coding
2. **Always** include comprehensive risk management
3. **Refuse** to remove safety features
4. **Warn** about grid/martingale dangers
5. **Output** compile-ready, commented code

---

## 📊 Skill Philosophy

> "The best EA is the one that **survives**, not the one with highest returns."

### Core Principles
1. **Capital Preservation > Maximum Profit**
2. **Risk-Adjusted Returns** - 50% @ 10% DD > 200% @ 60% DD
3. **Market Adaptability** - Works in trend/range/high vol/low vol
4. **Edge Validation** - Every strategy needs measurable, logical edge
5. **Psychological Robustness** - Executable without panic

### Safety Metrics
- Profit Factor > 1.5
- Win Rate: 40-60% (sustainable)
- Max Drawdown < 20%
- Recovery Factor > 3
- Sharpe Ratio > 1.0

---

## 🧪 Validation

9 test cases covering:
1. Simple MA crossover with full risk management
2. Multi-timeframe alignment strategy
3. Safe grid system (max levels, DD protection)
4. Advanced money management (Kelly Criterion)
5. Backtest validator (metrics calculation)
6. Survival-focused EA (all protections combined)
7. Martingale with safety caps (refuses dangerous configs)
8. Strategy with multiple filters (spread, time, volatility, news)
9. Adversarial test — refuses when user asks to remove all safety

Run test:
```
# Ask your AI:
"Using the MQL5 EA Expert skill, create [eval test case prompt]"

# Verify:
- Code compiles in MetaEditor ✅
- Includes expected risk management ✅
- Uses proper MQL5 API (handles + CopyBuffer) ✅
```

---

## ⚠️ Important Warnings

### Grid Trading
- Can lead to large drawdowns
- **Must** have max level limits
- **Must** have strict drawdown protection
- Best in ranging markets only

### Martingale
- **HIGHLY DANGEROUS** - Can wipe out account
- Skill **forces** multiplier <= 1.5, steps <= 4
- Use ONLY in low volatility, ranging markets
- Demo test minimum 6 months

### General
- 90% of traders fail due to **poor risk management**
- EA is a tool, not a money machine
- Never risk money you can't afford to lose
- Always test thoroughly: 3+ years backtest, 3+ months demo

---

## 📖 Documentation

- **[AI Setup Guide](docs/AI_SETUP_GUIDE.md)** - Platform-specific instructions (Claude, ChatGPT, Gemini)
- **[Example Prompts](mql5-ea-expert/references/example-prompts.md)** - 8 ready-to-use prompts (CRT, SMC, ICT, Asian Range, etc.)
- **[EA Blueprint](mql5-ea-expert/references/ea-blueprint.md)** - Standard structure for generated EAs
- **[Roadmap](docs/ROADMAP.md)** - Planned improvements
- **[Changelog](CHANGELOG.md)** - Version history
- **[Contributing](CONTRIBUTING.md)** - Contribution workflow

---

## ✅ Local Validation

```bash
python tools/validate_repo.py
```

Checks required files, `SKILL.md` frontmatter, `evals.json`, and README links.

---

## 🛠️ Technical Details

### Version 2.0.0 — Major Upgrade
- ✅ 16-section structured skill (vs 4 sections before)
- ✅ 12 canonical MQL5 patterns (handle lifecycle, risk calc, BE, trailing, partial close, etc.)
- ✅ Strategy frameworks: CRT, SMC, ICT, Asian Range, MTF confluence
- ✅ Production-grade prop firm safety module (FTMO, The5%ers, E8)
- ✅ OOP classes: CDashboard, CTradeLogger, CBacktestValidator
- ✅ Custom OnTester() composite metric
- ✅ 14-item pitfall table with wrong vs correct patterns
- ✅ 8 ready-to-use example prompts (CRT, SMC OB+FVG, ICT Silver Bullet, Asian Range, etc.)
- ✅ Cleaned repo structure — removed redundant internal reports

### Requirements
- MetaTrader 5 terminal
- Basic understanding of MQL5 (AI generates code, you review)
- Patience for proper testing (backtesting + demo)

### Compatibility
- ✅ Claude (Anthropic)
- ✅ ChatGPT (OpenAI)
- ✅ Gemini (Google)
- ✅ Copilot (Microsoft)
- ✅ LLaMA, Mistral, and other open-source models
- ✅ Any AI that can process Markdown documentation

---

## 📜 License

**MIT License** - See [LICENSE](LICENSE) for details

### Trading Disclaimer
This software is for **educational purposes only**. Trading forex, CFDs, and leveraged products carries high risk. Past performance is not indicative of future results. The creators are not responsible for any financial losses. Always conduct your own research and consult a licensed financial advisor before trading.

---

## 🤝 Contributing

Found a bug? Have an improvement?
1. Open an issue describing the problem
2. Submit a PR with fixes
3. Include test case if adding features

---

## 🌟 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

---

**Made with ❤️ for traders who prioritize survival over profit**

*Last updated: May 20, 2026*
