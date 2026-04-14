traded_stocks = set()


def is_traded(symbol):
    return symbol in traded_stocks


def mark_traded(symbol):
    traded_stocks.add(symbol)