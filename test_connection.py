from core.broker import connect_kite
from config.settings import ACCESS_TOKEN

kite = connect_kite(ACCESS_TOKEN)

profile = kite.profile()

print(profile)