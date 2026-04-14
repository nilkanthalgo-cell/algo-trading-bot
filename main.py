import signal
import sys

from core.auth import load_token, auto_login
from core.broker import connect_kite
from core.engine import start_engine
from core.stop import stop_event


def start():
    access_token = load_token()

    if access_token:
        kite = connect_kite(access_token)
        try:
            kite.profile()
            print("Login OK")
            return kite
        except:
            print("Token expired")

    access_token = auto_login()
    kite = connect_kite(access_token)

    print("Login OK")
    return kite


# ✅ Graceful shutdown
def shutdown_handler(sig, frame):
    print("\n🛑 Stopping system gracefully...")
    stop_event.set()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)

    kite = start()
    start_engine(kite)