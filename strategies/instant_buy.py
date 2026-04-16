import json
from core.broker import smart_buy
from core.trade_manager import is_traded, mark_traded

DATA_FILE = "data/strategy_data.json"


def run(kite):
    print("\n--- Instant Buy Strategy ---\n")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    strategy = data.get("instant_buy", {})

    if not strategy.get("enable", False):
        print("Instant Buy Disabled\n")
        return

    product = strategy.get("product", "MIS")

    for symbol, config in strategy.get("stocks", {}).items():
        if not config.get("enable", False):
            continue

        if is_traded("instant_buy", symbol):
            print(f"{symbol} already traded. Skipping...")
            continue

        qty = config.get("qty", 0)

        print(f"Buying {symbol} (Qty: {qty})")
        smart_buy(kite, symbol, qty, product)

        mark_traded("instant_buy", symbol)