import requests
import json
import time
import os
from datetime import datetime, timedelta

# ✅ BOT TOKEN DIRECT (no env file needed)
BOT_TOKEN = "8329971085:AAGMFNrS-2K4zDa9P7f7bsXHsVqJx6LRo6s"

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
DATA_FILE = "data.json"
POLL_INTERVAL = 2


# ✅ Ensure data.json exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


def load_data():
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)


def send_message(chat_id, text):
    url = URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Send message error:", e)


def get_updates(offset=None):
    url = URL + "getUpdates"
    params = {}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json()
    except Exception as e:
        print("Get updates error:", e)
        return {"ok": False, "result": []}


# ✅ User system
def ensure_user(chat_id):
    d = load_data()
    if str(chat_id) not in d:
        d[str(chat_id)] = {"costs": [], "usage": []}
        save_data(d)
    return d


def add_cost(chat_id, amount, service=None):
    d = load_data()
    ensure_user(chat_id)
    entry = {
        "amount": float(amount),
        "service": service if service else "General",
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    }
    d[str(chat_id)]["costs"].append(entry)
    save_data(d)
    return entry


def add_usage(chat_id, service, amount_unit):
    d = load_data()
    ensure_user(chat_id)
    entry = {
        "service": service,
        "usage": amount_unit,
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    }
    d[str(chat_id)]["usage"].append(entry)
    save_data(d)
    return entry


def reset_user(chat_id):
    d = load_data()
    d[str(chat_id)] = {"costs": [], "usage": []}
    save_data(d)


# ✅ Prediction Logic
def predict_next_week(chat_id):
    d = load_data()
    user = d.get(str(chat_id), {"costs": []})
    costs = user.get("costs", [])

    if not costs:
        return None

    today = datetime.utcnow().date()
    last_7_total = 0
    days = 0

    for entry in costs:
        dt = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if (today - dt).days <= 7:
            last_7_total += float(entry["amount"])
            days += 1

    if days == 0:
        days = 1

    avg_daily = last_7_total / days
    predicted = round(avg_daily * 7 * 1.2, 2)

    return {
        "predicted_week": predicted,
        "avg_daily": round(avg_daily, 2)
    }


# ✅ Command Handler
def handle_command(chat_id, text):
    parts = text.strip().split()
    cmd = parts[0].lower()

    if cmd == "/start":
        send_message(chat_id, "✅ Bot is active!\nType /help")
        return

    if cmd == "/help":
        send_message(chat_id,
            "Commands:\n"
            "/addcost <amount>\n"
            "/predict\n"
            "/reset"
        )
        return

    if cmd == "/addcost":
        if len(parts) < 2:
            send_message(chat_id, "Usage: /addcost <amount>")
            return
        amt = float(parts[1])
        add_cost(chat_id, amt)
        send_message(chat_id, f"✅ Added ₹{amt}")
        return

    if cmd == "/predict":
        res = predict_next_week(chat_id)
        if not res:
            send_message(chat_id, "No data found.")
            return
        send_message(chat_id,
            f"📈 Weekly Prediction: ₹{res['predicted_week']}\n"
            f"Avg/day: ₹{res['avg_daily']}"
        )
        return

    if cmd == "/reset":
        reset_user(chat_id)
        send_message(chat_id, "✅ Data reset.")
        return

    send_message(chat_id, "Unknown command")


# ✅ Main Bot Loop
def main():
    print("✅ Bot Running... Polling Started")
    last_update_id = None

    while True:
        updates = get_updates(offset=last_update_id + 1 if last_update_id else None)

        if updates.get("result"):
            for upd in updates["result"]:
                last_update_id = upd["update_id"]
                msg = upd.get("message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                print(f"{datetime.utcnow()} - {chat_id} - {text}")

                if text.startswith("/"):
                    handle_command(chat_id, text)
                else:
                    send_message(chat_id, "Type /help")

        time.sleep(2)


if __name__ == "__main__":
    main()
