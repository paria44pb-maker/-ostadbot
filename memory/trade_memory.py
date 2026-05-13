# trade_memory.py
# ذخیره حافظه معاملات

import json
import os

MEMORY_FILE = "memory/trades.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_trade(trade_data):

    memory = load_memory()

    memory.append(trade_data)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def last_trades(limit=5):

    memory = load_memory()

    return memory[-limit:]
