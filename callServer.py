import requests 

def callPlayers():
    playersRes = requests.get("https://tapi.socomcommunity.com/api/universes/players?applicationId=10684")
    info = playersRes.json()
    return info

def callGames():
    gameRes = requests.get("https://tapi.socomcommunity.com/api/rooms/68")
    gameInfo = gameRes.json()
    return gameInfo

