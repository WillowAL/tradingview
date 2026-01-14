# tradingview
TradingView strategies library

Structure:
- `strategies/`: Pine Script strategies (`.pine`)
- `scripts/pine_lint.py`: basic pre-check for quotes, comments, and brackets

Quick checks:
- `python3 scripts/pine_lint.py`

Pre-commit hook (local only):
- `.git/hooks/pre-commit` runs `scripts/pine_lint.py` before each commit

Strategy header requirement:
- Every new/updated Pine file must start with this header (fill in values):
```pine
//@version=5
// STRATEGY_ID:
// State: STABLE / LIVE_SAFE / BACKTEST_CLEAN / EXPERIMENT / ARCHIVE
// DATE: YYYY-MM-DD
// Features:
// NOTES: ...
```
