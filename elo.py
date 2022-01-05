from discord import team


def getExpected(r1, r2):
    r1 = 10**(r1/400)
    r2 = 10**(r2/400)

    e1 = r1/(r1+r2)
    e2 = r2/(r1+r2)

    return e1, e2

def getLobbyElos(elos, lobby):
    length = len(lobby)
    middle_index = length//2

    red = lobby[:middle_index]
    blue = lobby[middle_index:]

    red_elo, blue_elo = 0, 0
    for player in red:
        red_elo+=elos[player]
    red_elo
    for player in blue:
        blue_elo+=elos[player]
    blue_elo

    return red_elo, blue_elo

def getTeamElo(elos, team):
    team_elo = 0
    for player in team:
        team_elo+=elos[player]
    return team_elo
