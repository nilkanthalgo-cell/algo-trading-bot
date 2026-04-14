from main import start
from core.broker import smart_buy

kite = start()

smart_buy(kite, "INFY", 1)