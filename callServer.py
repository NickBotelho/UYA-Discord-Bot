import requests


def callPlayers():
 
    playersRes = requests.get("https://tapi.socomcommunity.com/api/universes/players?applicationId=10684")
    try:
        playersRes.raise_for_status() #throws error if API gets fucked up 
        info = playersRes.json()
        return info
    except: 
        return "error"



def callGames():
    gameRes = requests.get("https://tapi.socomcommunity.com/api/rooms/68")
    try:
        gameRes.raise_for_status()
        gameInfo = gameRes.json()
        return gameInfo
    except:
        return "error"

