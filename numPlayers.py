def numPlayers(info):
    res = "Nobody is online." if len(info) == 0 else "There are {} players online.".format(len(info))
    return res