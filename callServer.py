import requests


def callPlayers():
 
    playersRes = requests.get("https://uya.raconline.gg/tapi/robo/players")
    try:
        playersRes.raise_for_status() #throws error if API gets fucked up 
        info = playersRes.json()
        return info
    except: 
        return "error"



def callGames():
    gameRes = requests.get("https://s2api.socomcommunity.com/api/rooms/68")
    try:
        gameRes.raise_for_status()
        gameInfo = gameRes.json()
        return gameInfo
    except:
        return "error"

