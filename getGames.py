def getGames(info):
    res = "No Games :(" if len(info) == 0 else "Current Games:\n"
    for game in info:
        host = game['players'][0]['name'] #grab host name
        host+= "'s"
        res+= "{}, Occupancy: ({}/{})\n".format(host, game['playerCount'], game['maxPlayers'])
    return res


    
