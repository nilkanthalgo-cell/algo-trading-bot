import json
import time
import pandas as pd
from datetime import datetime, timedelta
from core.broker import smart_buy
from core.trade_manager import is_traded, mark_traded
from core.stop import stop_event

DATA_FILE = "data/strategy_data.json"

TIMEFRAME = "15minute"


def get_instrument_token(kite, symbol):
    instruments = kite.instruments("NSE")

    for inst in instruments:
        if inst["tradingsymbol"] == symbol:
            return inst["instrument_token"]

    return None


def get_candles(kite, symbol):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=10)

    token = get_instrument_token(kite, symbol)

    data = kite.historical_data(
        instrument_token=token,
        from_date=from_date,
        to_date=to_date,
        interval=TIMEFRAME
    )

    return pd.DataFrame(data)


def calculate_ema(df, period=200):
    df["ema"] = df["close"].ewm(span=period).mean()
    return df


def check_touch(df):
    last = df.iloc[-1]
    return last["low"] <= last["ema"] <= last["high"]


def run(kite):
    print("\n--- EMA Strategy ---\n")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    strategy = data.get("ema_strategy", {})

    if not strategy.get("enable", False):
        print("EMA Strategy Disabled\n")
        return

    product = strategy.get("product", "MIS")
    stocks = strategy.get("stocks", {})

    while not stop_event.is_set():
        print("\nChecking EMA...\n")

        for symbol, config in stocks.items():
            if not config.get("enable", False):
                continue

            if is_traded(symbol):
                print(f"{symbol} already traded. Skipping...")
                continue

            qty = config.get("qty", 0)

            try:
                df = get_candles(kite, symbol)

                if df.empty:
                    continue

                df = calculate_ema(df)

                if check_touch(df):
                    print(f"{symbol} EMA TOUCH → BUY")
                    smart_buy(kite, symbol, qty, product)
                    mark_traded(symbol)
                else:
                    print(f"{symbol} no touch")

            except Exception as e:
                print(f"{symbol} error: {e}")

        time.sleep(10)

    print("EMA Strategy Stopped")