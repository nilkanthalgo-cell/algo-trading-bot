import json
import time
from datetime import datetime
from core.broker import smart_buy, smart_sell, get_ltp
from core.trade_manager import is_traded, mark_traded
from core.stop import stop_event

DATA_FILE = "data/strategy_data.json"

TARGET_PCT = 2
STOPLOSS_PCT = 2


# 🔥 =========================
# 🔥 CHANGE TIME HERE (ENTRY)
# 🔥 =========================
ENTRY_HOUR = 9
ENTRY_MINUTE = 20
# Example:
# ENTRY_HOUR = 13
# ENTRY_MINUTE = 45


# 🔥 =========================
# 🔥 CHANGE TIME HERE (EXIT)
# 🔥 =========================
EXIT_HOUR = 9
EXIT_MINUTE = 30
# Example:
# EXIT_HOUR = 14
# EXIT_MINUTE = 0


def wait_until(hour, minute):
    while not stop_event.is_set():
        now = datetime.now()
        if now.hour == hour and now.minute >= minute:
            break
        time.sleep(2)


def run(kite):
    print("\n--- Morning Trade Strategy ---\n")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    strategy = data.get("morning_trade", {})

    if not strategy.get("enable", False):
        print("Morning Trade Disabled\n")
        return

    product = strategy.get("product", "MIS")
    stocks = strategy.get("stocks", {})

    # 🔥 WAIT FOR ENTRY TIME
    print(f"Waiting for {ENTRY_HOUR}:{ENTRY_MINUTE}...")
    wait_until(ENTRY_HOUR, ENTRY_MINUTE)

    if stop_event.is_set():
        return

    positions = {}

    # 🔥 BUY AT ENTRY TIME
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

    print(f"\nMonitoring until {EXIT_HOUR}:{EXIT_MINUTE}...\n")

    # 🔥 MONITOR LOOP
    while not stop_event.is_set():
        now = datetime.now()

        for symbol, pos in positions.items():
            if not pos["active"]:
                continue

            ltp = get_ltp(kite, symbol)
            entry = pos["entry"]

            change = ((ltp - entry) / entry) * 100

            print(f"{symbol} | {ltp} | {change:.2f}%")

            # ✅ TARGET
            if change >= TARGET_PCT:
                print(f"{symbol} Target Hit")
                smart_sell(kite, symbol, pos["qty"], product)
                pos["active"] = False

            # ✅ STOPLOSS
            elif change <= -STOPLOSS_PCT:
                print(f"{symbol} Stoploss Hit")
                smart_sell(kite, symbol, pos["qty"], product)
                pos["active"] = False

            # 🔥 FORCE EXIT AT EXIT TIME
            elif now.hour == EXIT_HOUR and now.minute >= EXIT_MINUTE:
                print(f"{symbol} Time Exit ({EXIT_HOUR}:{EXIT_MINUTE})")
                smart_sell(kite, symbol, pos["qty"], product)
                pos["active"] = False

        time.sleep(2)

    print("Morning Strategy Stopped")