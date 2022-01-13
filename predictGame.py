from mongodb import Database
from itertools import permutations, combinations
import pickle
import pandas as pd
import numpy as np
import uya_encodings
# player_stats = Database("UYA","Player_Stats")
# players_online = Database("UYA","Players_Online")
# game_history = Database("UYA", "Game_History")
# games_active = Database("UYA","Games_Active")

# model_filename = 'uya_game_prediction(all modes).sav'
# loaded_model = pickle.load(open(model_filename, 'rb'))

def getTeamInformation(team, player_stats):
    info = {
        'k/d':0,
        'w/l':0,
        'caps/gm':0,
        # 'saves/gm':0,
        'kills/gm':0,
        'baseDmg/gm':0,
        'kills/min':0,
        'deaths/min':0,
        'suicides/min':0,
        # 'caps/min':0,
        'saves/min':0,
        # 'flux kills/min':0,
        # 'blitz kills/min':0,
        # 'grav kills/min':0,

        'elo':0,
    }
    for player in team:
        name = player

        player = player_stats.collection.find_one({'username':player})
        advanced = player['advanced_stats']
        player = player['stats']
        

        info['k/d'] = info['k/d'] + (player['overall']['kills'] / player['overall']['deaths']) if player['overall']['deaths'] > 0 else info['k/d'] 
        info['w/l'] = info['w/l'] + (player['overall']['wins'] / player['overall']['losses']) if player['overall']['losses'] > 0 else info['w/l'] 
        info['kills/gm'] = info['kills/gm'] +  (player['overall']['kills'] / player['overall']['games_played']) if player['overall']['games_played'] > 0 else info['kills/gm'] 
        info['caps/gm'] = info['caps/gm'] + (player['ctf']['ctf_caps'] / (player['ctf']['ctf_wins'] + player['ctf']['ctf_losses'])) \
            if (player['ctf']['ctf_wins'] + player['ctf']['ctf_losses']) > 0 else info['caps/gm']
        # info['saves/gm'] = info['saves/gm'] + (player['ctf']['ctf_saves'] / (player['ctf']['ctf_wins'] + player['ctf']['ctf_losses'])) \
        #     if (player['ctf']['ctf_wins'] + player['ctf']['ctf_losses']) > 0 else info['saves/gm']
        info['baseDmg/gm'] = info['baseDmg/gm'] +  (player['overall']['overall_base_dmg'] / player['overall']['games_played']) if player['overall']['games_played'] > 0 else info['baseDmg/gm'] 

        info['kills/min'] = info['kills/min'] + advanced['per_min']['kills/min']
        info['deaths/min'] = info['deaths/min'] + advanced['per_min']['deaths/min']
        info['suicides/min'] = info['suicides/min'] + advanced['per_min']['suicides/min']
        # info['caps/min'] = info['caps/min'] + advanced['per_min']['caps/min']
        info['saves/min'] = info['saves/min'] + advanced['per_min']['saves/min']
        # info['flux kills/min'] = info['flux kills/min'] + advanced['per_min']['flux_kills/min']
        # info['blitz kills/min'] = info['blitz kills/min'] + advanced['per_min']['blitz_kills/min']
        # info['grav kills/min'] = info['grav kills/min'] + advanced['per_min']['gravity_bomb_kills/min']
        info['elo'] += advanced['elo']['overall']

        

    info['k/d'] = round((info['k/d'] / len(team)), 2)
    info['w/l'] = round((info['w/l'] / len(team)), 2)
    info['kills/gm'] = round((info['kills/gm'] / len(team)), 2)
    info['caps/gm'] = round((info['caps/gm'] / len(team)), 2)
    # info['saves/gm'] = round((info['saves/gm'] / len(team)), 2)
    info['baseDmg/gm'] = round((info['baseDmg/gm'] / len(team)), 2)
    info['kills/min'] = round((info['kills/min'] / len(team)), 2)
    info['deaths/min'] = round((info['deaths/min'] / len(team)), 2)
    info['suicides/min'] = round((info['suicides/min'] / len(team)), 2)
    # info['caps/min'] = round((info['caps/min'] / len(team)), 2)
    info['saves/min'] = round((info['saves/min'] / len(team)), 2)
    # info['flux kills/min'] = round((info['flux kills/min'] / len(team)), 2)
    # info['blitz kills/min'] = round((info['blitz kills/min'] / len(team)), 2)
    # info['grav kills/min'] = round((info['grav kills/min'] / len(team)), 2)
    info['elo'] = round(info['elo'] / len(team), 2)

    return info
def normalize(winner, loser):
    win = 1 if winner > loser else (round(winner/loser, 2)  if loser > 0 else 0)
    loss = 1 if loser > winner else (round(loser/winner, 2) if winner > 0 else 0)
    return win, loss

def predictGame(game, model, player_stats):

    lobby = []
    for name in game['details']['players']:
            lobby.append(name)

    lobby = set(lobby)
    possible_teams = combinations(lobby, len(lobby)//2)

    best = 100
    best_teams = None
    for red in list(possible_teams):
        blue = [name for name in lobby if name not in red]

        gamemode = uya_encodings.GAMEMODES[game['details']['gamemode']]
        map = uya_encodings.MAPS[game['details']['map']]
        red_info = getTeamInformation(red, player_stats)
        blue_info = getTeamInformation(blue, player_stats)

        
        data = np.array(list(red_info.values()))
        data = data.astype(np.double)
        red_x = data

        data = np.array(list(blue_info.values()))
        data = data.astype(np.double)
        blue_x = data

        for i, (redi, bluei) in enumerate(zip(red_x, blue_x)):
            red_x[i], blue_x[i] = normalize(redi, bluei)

        red_x = np.append(red_x, [gamemode, map])
        blue_x = np.append(blue_x, [gamemode, map])

        red_x = red_x.reshape(1, -1)
        blue_x = blue_x.reshape(1, -1)
        red_proba= model.predict_proba(red_x)
        blue_proba = model.predict_proba(blue_x)

        # diff = abs(red_proba[0,1] - blue_proba[0,1])
        diff = abs(1 - (red_proba[0,1] + blue_proba[0,0]))
        if diff < best:
            best_teams = red, blue
            best = diff
            best_probs = red_proba, blue_proba
            best_info = red_x, blue_x

    red_p, blue_p = best_probs[0][0,1], best_probs[1][0,1]
    total = red_p+blue_p
    return best_teams, [red_p/total, blue_p/total]

def predictAll(game, model, player_stats):

    lobby = []
    for name in game['details']['players']:
            lobby.append(name)

    lobby = set(lobby)
    possible_teams = combinations(lobby, len(lobby)//2)

    teams, probs = [], []
    for red in list(possible_teams):
        blue = [name for name in lobby if name not in red]

        gamemode = uya_encodings.GAMEMODES[game['details']['gamemode']]
        map = uya_encodings.MAPS[game['details']['map']]
        red_info = getTeamInformation(red, player_stats)
        blue_info = getTeamInformation(blue, player_stats)

        
        data = np.array(list(red_info.values()))
        data = data.astype(np.double)
        red_x = data

        data = np.array(list(blue_info.values()))
        data = data.astype(np.double)
        blue_x = data

        for i, (redi, bluei) in enumerate(zip(red_x, blue_x)):
            red_x[i], blue_x[i] = normalize(redi, bluei)

        red_x = np.append(red_x, [gamemode, map])
        blue_x = np.append(blue_x, [gamemode, map])

        red_x = red_x.reshape(1, -1)
        blue_x = blue_x.reshape(1, -1)
        red_proba= model.predict_proba(red_x)
        blue_proba = model.predict_proba(blue_x)


        teams.append(red)
        probs.append(red_proba[0,1])

    return teams, probs

def getInfoSummary(info):
    res = '''
K/D = {}
W/L = {}
Kills/Gm = {}
Caps/Gm = {}
Base Damage/Gm = {}
Elo = {}'''.format(info['k/d'],info['w/l'],info['kills/gm'],info['caps/gm'],info['baseDmg/gm'],info['elo'])
    return res
