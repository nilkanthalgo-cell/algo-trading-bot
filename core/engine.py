import threading
import json

from strategies.instant_buy import run as instant_buy
from strategies.time_trade import run as time_trade
from strategies.ema_strategy import run as ema_strategy
from strategies.morning_trade import run as morning_trade

DATA_FILE = "data/strategy_data.json"


def run_strategy(func, kite):
    thread = threading.Thread(target=func, args=(kite,))
    thread.start()


def start_engine(kite):
    print("\n🚀 Starting Trading Engine...\n")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Instant Buy (run once)
    if data.get("instant_buy", {}).get("enable", False):
        run_strategy(instant_buy, kite)

    # Time Strategy (parallel)
    if data.get("time_trade", {}).get("enable", False):
        run_strategy(time_trade, kite)

    # EMA Strategy (parallel)
    if data.get("ema_strategy", {}).get("enable", False):
        run_strategy(ema_strategy, kite)

    if data.get("morning_trade", {}).get("enable", False):
        run_strategy(morning_trade, kite)