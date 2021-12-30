import discord
import requests
from requests.api import get
ALT_API = 'https://uya.raconline.gg/tapi/robo/alts'

def getAlts(username):
    url = f"{ALT_API}/{username}"
    res = requests.get(url)
    res = res.json()
    

    if res != '[]':
        alts = ''
        for alt in res:
            alts+=f"- {alt}\n"
    else:
        alts = "Player NOT found...It just started tracking so maybe if you actually got on, you'd be in here"

    embed = discord.Embed(
    title = f"Accounts for: {username}",
    description = alts,
    color=11043122
    )
    return embed


# getAlts("asdf")
# getAlts("aequs")
