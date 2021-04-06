def getGames(info):
    res = "No Games :(" if len(info) == 0 else "Current Games:\n"
    for game in info:
        s = game['name'].split()
        res+= "{}, Occupancy: ({}/{})\n".format(s[0], game['playerCount'], game['maxPlayers'])
    return res

