import json
import time
from datetime import datetime
from core.broker import smart_buy, smart_sell, get_ltp
from core.trade_manager import is_traded, mark_traded
from core.stop import stop_event

DATA_FILE = "data/strategy_data.json"

TARGET_PCT = 2
STOPLOSS_PCT = 2


def wait_until(hour, minute):
    while not stop_event.is_set():
        now = datetime.now()
        if now.hour == hour and now.minute >= minute:
            break
        time.sleep(2)


def run(kite):
    print("\n--- Time Trade Strategy ---\n")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    strategy = data.get("time_trade", {})

    if not strategy.get("enable", False):
        print("Time Trade Disabled\n")
        return

    product = strategy.get("product", "MIS")
    stocks = strategy.get("stocks", {})

    print("Waiting for 9:30...")
    wait_until(9, 30)

    if stop_event.is_set():
        return

    positions = {}

    for symbol, config in stocks.items():
        if not config.get("enable", False):
            continue

        if is_traded(symbol):
            print(f"{symbol} already traded. Skipping...")
            continue

        qty = config.get("qty", 0)

        smart_buy(kite, symbol, qty, product)
        entry = get_ltp(kite, symbol)

        positions[symbol] = {
            "qty": qty,
            "entry": entry,
            "active": True
        }

        mark_traded(symbol)
        print(f"{symbol} bought at {entry}")

    print("\nMonitoring...\n")

    while not stop_event.is_set():
        now = datetime.now()

        for symbol, pos in positions.items():
            if not pos["active"]:
                continue

            ltp = get_ltp(kite, symbol)
            entry = pos["entry"]

            change = ((ltp - entry) / entry) * 100

            print(f"{symbol} | {ltp} | {change:.2f}%")

            if change >= TARGET_PCT:
                print(f"{symbol} Target Hit")
                smart_sell(kite, symbol, pos["qty"], product)
                pos["active"] = False

            elif change <= -STOPLOSS_PCT:
                print(f"{symbol} Stoploss Hit")
                smart_sell(kite, symbol, pos["qty"], product)
                pos["active"] = False

            elif now.hour == 15 and now.minute >= 15:
                print(f"{symbol} Time Exit")
                smart_sell(kite, symbol, pos["qty"], product)
                pos["active"] = False

        time.sleep(3)

    print("Time Trade Strategy Stopped")