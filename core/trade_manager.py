traded = set()


def is_traded(strategy, symbol):
    return (strategy, symbol) in traded


def mark_traded(strategy, symbol):
    traded.add((strategy, symbol))