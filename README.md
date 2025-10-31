# CC-Prediction-Bot

A Python-based AWS Cloud Cost Prediction Telegram Bot that stores daily cost entries locally (JSON) and predicts the next 7 days using a simple averaging model.

## Features
- `/start` — Start the bot
- `/help` — List commands
- `/addcost <amount>` — Add daily cloud cost (₹)
- `/predict` — Predict next week's cost
- `/reset` — Clear user data
- Stores data in local `data.json`

## Tech stack
- Python 3
- Telegram Bot API
- requests
- Local JSON storage (optional: extend to AWS)

## Quick start (local)
1. Clone repo or download files
2. Create `.env` (see below)
3. `pip install -r requirements.txt`
4. `python CC_bot_fixed.py`

## .env (local only)
Create a file named `.env` next to the `.py` file with:
**Do not** push `.env` to GitHub. `.gitignore` already excludes it.

## License
MIT (or change if you prefer)
