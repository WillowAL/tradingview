# tradingview
TradingView strategies library

Structure:
- `strategies/`: Pine Script strategies (`.pine`)
- `scripts/pine_lint.py`: basic pre-check for quotes, comments, and brackets

Quick checks:
- `python3 scripts/pine_lint.py`

Pre-commit hook (local only):
- `.git/hooks/pre-commit` runs `scripts/pine_lint.py` before each commit
