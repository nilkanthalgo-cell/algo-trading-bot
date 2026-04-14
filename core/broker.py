from kiteconnect import KiteConnect
from datetime import datetime, time
from config.settings import API_KEY, EXCHANGE


def connect_kite(access_token):
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(access_token)
    return kite


def is_market_open():
    now = datetime.now().time()
    return time(9, 15) <= now <= time(15, 30)


def get_ltp(kite, symbol):
    data = kite.ltp(f"{EXCHANGE}:{symbol}")
    return data[f"{EXCHANGE}:{symbol}"]["last_price"]


# ✅ SMART BUY (with product control)
def smart_buy(kite, symbol, qty, product):
    try:
        if is_market_open():
            order_id = kite.place_order(
                variety="regular",
                exchange=EXCHANGE,
                tradingsymbol=symbol,
                transaction_type="BUY",
                quantity=qty,
                product=product,
                order_type="MARKET",
            )
            print(f"MARKET BUY ({product}): {symbol}")
            return order_id

        else:
            ltp = get_ltp(kite, symbol)
            price = round(ltp + 1, 2)

            order_id = kite.place_order(
                variety="amo",
                exchange=EXCHANGE,
                tradingsymbol=symbol,
                transaction_type="BUY",
                quantity=qty,
                product=product,
                order_type="LIMIT",
                price=price,
            )
            print(f"AMO BUY ({product}): {symbol} @ {price}")
            return order_id

    except Exception as e:
        print(f"BUY error ({symbol}): {e}")


# ✅ SMART SELL (with product control)
def smart_sell(kite, symbol, qty, product):
    try:
        if is_market_open():
            order_id = kite.place_order(
                variety="regular",
                exchange=EXCHANGE,
                tradingsymbol=symbol,
                transaction_type="SELL",
                quantity=qty,
                product=product,
                order_type="MARKET",
            )
            print(f"MARKET SELL ({product}): {symbol}")
            return order_id

        else:
            ltp = get_ltp(kite, symbol)
            price = round(ltp - 1, 2)

            order_id = kite.place_order(
                variety="amo",
                exchange=EXCHANGE,
                tradingsymbol=symbol,
                transaction_type="SELL",
                quantity=qty,
                product=product,
                order_type="LIMIT",
                price=price,
            )
            print(f"AMO SELL ({product}): {symbol} @ {price}")
            return order_id

    except Exception as e:
        print(f"SELL error ({symbol}): {e}")