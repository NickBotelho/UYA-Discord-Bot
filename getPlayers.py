import time
from callServer import callGames, callPlayers
from mongodb import Database
def getPlayers(res):
    players = "Players Online:\n"
    for player in res:
        players+= "-"+player["name"] +"\n"
    return players


def updateOnline(db,online):
    res = callPlayers()
    if res != "error":
        still_on = []
        for player in res:
            name = player["name"]
            still_on.append(name)
            if not name in online:
                online[name] = time.time()
                db.addToDB(name)

        
        if len(still_on) != len(online.keys()):
            keys = online.keys()
            offline = []
            for p in keys:
                if not p in still_on:
                    db.logPlayerOff(online, p)
                    offline.append(p)
            for p in offline:
                del online[p]
        return online