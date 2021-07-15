import requests
from toLadderstatswide import HextoLadderstatswide, bytes_field
res= requests.get('https://uya.raconline.gg/tapi/robo/players')
res = res.json()
for p in res:
    print(p['username'])
