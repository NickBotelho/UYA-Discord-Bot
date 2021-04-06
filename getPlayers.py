def getPlayers(res):
    players = "Players Online:\n"
    for player in res:
        players+= "-"+player["name"] +"\n"
    return players