from kiteconnect import KiteConnect
from datetime import datetime, time
from config.settings import API_KEY, EXCHANGE


def connect_kite(access_token):
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(access_token)
    return kite


# ✅ Check market hours
def is_market_open():
    now = datetime.now().time()
    return time(9, 15) <= now <= time(15, 30)


# ✅ Get LTP
def get_ltp(kite, symbol):
    data = kite.ltp(f"{EXCHANGE}:{symbol}")
    return data[f"{EXCHANGE}:{symbol}"]["last_price"]


# ✅ SMART BUY (FIXED)
def smart_buy(kite, symbol, qty, product):
    try:
        ltp = get_ltp(kite, symbol)
        price = round(ltp + 0.5, 2)   # small buffer

        variety = "regular" if is_market_open() else "amo"

        kite.place_order(
            variety=variety,
            exchange=EXCHANGE,
            tradingsymbol=symbol,
            transaction_type="BUY",
            quantity=qty,
            product=product,
            order_type="LIMIT",
            price=price,
        )

        print(f"{variety.upper()} BUY ({product}): {symbol} @ {price}")
        return True

    except Exception as e:
        print(f"BUY error ({symbol}): {e}")
        return False

# ✅ SMART SELL (FIXED + ADDED)
def smart_sell(kite, symbol, qty, product):
    try:
        ltp = get_ltp(kite, symbol)
        price = round(ltp - 0.5, 2)

        variety = "regular" if is_market_open() else "amo"

        kite.place_order(
            variety=variety,
            exchange=EXCHANGE,
            tradingsymbol=symbol,
            transaction_type="SELL",
            quantity=qty,
            product=product,
            order_type="LIMIT",
            price=price,
        )

        print(f"{variety.upper()} SELL ({product}): {symbol} @ {price}")
        return True

    except Exception as e:
        print(f"SELL error ({symbol}): {e}")
        return False