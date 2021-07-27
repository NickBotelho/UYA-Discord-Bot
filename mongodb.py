import pymongo
from pymongo import MongoClient
import time
from config import MongoPW, MongoUser
import os

try:
    if not MongoPW or not MongoUser:
        print('trying to get environment vars')
        MongoPW = os.environ["MongoPw"]
        MongoUser = os.environ["MongoUser"]
except:
    print(MongoPW, MongoUser)
    print('failed to load credentials')
    exit(1)
class Database():
    def __init__(self,db,collection):
        if db != "UYA":
            self.client = pymongo.MongoClient("mongodb+srv://Nick:noKAfcSGApcIQblv@cluster0.yhf0e.mongodb.net/UYA-Bot?retryWrites=true&w=majority")
        else:
            self.client = pymongo.MongoClient("mongodb+srv://{}:{}@cluster0.jydx7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(MongoUser, MongoPW))
        self.db = self.client[db]
        self.collection = self.db[collection]
    def getDB(self):
        return self.db
    def getCollection(self):
        return self.collection
    def addToDB(self, name):
        
        player = self.collection.find_one({"name":name})
        if player == None:
            self.collection.insert(
                {
                    "name":name,
                    "numLogins":1,
                    "time_minutes":0,
                    "time_hours":0            
                }
            )
        else:
            
            logins = int(player['numLogins'])
            logins+=1
            self.collection.find_one_and_update(
                {
                    "_id":player["_id"]
                },
                {
                    "$set":{
                        "numLogins":logins
                    }
                }
            )
    def logPlayerOff(self, online, name):
        player = self.collection.find_one({"name":name})   
        start = online[name]
        fin = time.time()
        id = player["_id"]
        session_time = int((abs(start-fin)/60))
        total_time = float(player["time_minutes"])
        total_time_hours = total_time/60
        self.collection.find_one_and_update(
            {
                "_id":id
            },
            {
                "$set":{
                    "time_minutes": (total_time + session_time),
                    "time_hours": (total_time_hours + (session_time/60))
                    }
            }
        )
    def updateTime(self, player, time):
        self.collection.find_one_and_update(
                {
                    "_id":player["_id"]
                },
                {
                    "$set":{
                        "time_minutes":time,
                        "time_hours":time/60
                    }
                }
            )
    def getTime(self,name, online):
        player = self.collection.find_one({"name":name})
        if player != None:
            if name in online: #if the player is online, we'll update in real time
                startTime = online[name]
                currentTime = time.time()
                currentTime = abs(currentTime - startTime) / 60 #current session time in minutes
                storedTime = float(player["time_minutes"])
                storedTime+= currentTime
                self.updateTime(player, storedTime)
                online[name] = time.time()
                player = self.collection.find_one({"name":name})
            storedTime = int(player["time_minutes"])
            if storedTime <= 60:
                return "{} Minutes.".format(storedTime)
            else:
                return "{:.1f} Hours".format(player['time_hours'])
        return None
    def addToSmokeLine(self, name, mention, time):
        player = self.collection.find_one({"name":name})
        if player == None:
            self.collection.insert(
                {
                    "name":name,
                    "discord_mention":mention,
                    "enter_time":time
                }
            )
        else:
            self.collection.find_one_and_update( #reset their time
                {
                    "_id":player["_id"]
                },
                {
                    "$set":{
                        "enter_time":time
                    }
                }
            )
    def getSmokersFromDB(self):
        smokeLine = {}
        smokePing = {}
        for person in self.collection.find():
            smokeLine[person['name']] = person['enter_time']
            smokePing[person['name']] = person['discord_mention']
        return smokeLine, smokePing
    def deleteSmoker(self, name):
        self.collection.delete_one({"name":name})
    def getTop10(self, stat):
        res = "NAME\t\t\tHOURS\n"
        i = 0
        for player in self.collection.find().sort([(stat,-1)]):
            if i < 10:
                i+=1
                res +="{}. {}\t {:.1f}\n".format(i, player['name'], player['time_hours'])
        return res
    def updateOnlinePlayers(self, onlinePlayers, time):
        currently_online = []
        for name in onlinePlayers:
            currently_online.append(name)
            player = self.collection.find_one({"name":name})
            if player == None:
                self.collection.insert(
                    {
                        "name":name,                       
                        "enter_time":time
                    }
                )
            else:
                self.collection.find_one_and_update( #reset their time
                    {
                        "_id":player["_id"]
                    },
                    {
                        "$set":{
                            "enter_time":time
                        }
                    }
                )
        for player in self.collection.find():
            if player['name'] not in currently_online:
                self.deleteSmoker(player['name'])
    def getOnlinePlayers(self):
        res = ['' for player in range(self.collection.count())]
        for i, player in enumerate(self.collection.find()):
            res[i] = player
        return res
    def getActiveGames(self):
        '''return a list of mongo documents from the active games collection'''
        res = ['' for player in range(self.collection.count())]
        for i, game in enumerate(self.collection.find()):
            res[i] = game
        return res
    def getUsername(self, id):
        return self.collection.find_one({'account_id':id})['username']
    def getPlayerBasicStats(self, username):
        username=username.lower().strip()
        player = self.collection.find_one({'username_lowercase':username})
        res = player['stats']['overall']
        return res
    def getPlayerAdvancedStats(self, username):
        username=username.lower().strip()
        player = self.collection.find_one({'username_lowercase':username})
        overall = player['stats']['overall']
        ctf = player['stats']['ctf']
        weapons = player['stats']['weapons']
        kills=overall['kills']
        deaths=overall['deaths']
        wins=overall['wins']
        losses=overall['losses']
        flux_kills=weapons['flux_kills']
        blitz_kills=weapons['blitz_kills']
        caps = ctf['ctf_caps']
        saves = ctf['ctf_saves']
        res = {
            'k/d':round(kills/deaths,2),
            'w/l':round(wins/losses,2),
            'caps':caps,
            'saves':saves,
            'flux_usage':(round(flux_kills/kills, 2) * 100),
            'flux/blitz':round(flux_kills/blitz_kills, 2)
        }
        return res
    def exists(self, username):
        username=username.lower().strip()
        player = self.collection.find_one({'username_lowercase':username})
        return player != None
    def getRealName (self, username):
        username=username.lower().strip()
        player = self.collection.find_one({'username_lowercase':username})
        return None if player == None else player['username']
    def updateDiscordAnalytics(self, commands):
        '''commands is a list of the number of calls for a given command
        0 = online calls
        1 = game calls
        2 = basic stats
        3 = advanced stats'''
        entry = self.collection.find_one({"name":"Discord Bot"})
        if entry == None:
            self.collection.insert_one(
                {
                    "name":"Discord Bot",
                    'online_calls':0,
                    'game_calls':0,
                    'basic_stat_calls':0,            
                    'advanced_stat_calls':0
                }
            )
        else:
            
            onlineCalls = int(entry['online_calls'])
            onlineCalls+=commands[0]
            gameCalls = int(entry['game_calls'])
            gameCalls+=commands[1]
            basicStatCalls = int(entry['basic_stat_calls'])
            basicStatCalls += commands[2]
            advancedStatCalls = int(entry['advanced_stat_calls'])
            advancedStatCalls += commands[3]
            self.collection.find_one_and_update(
                {
                    'name':"Discord Bot"
                },
                {
                    "$set":{
                        'online_calls':onlineCalls,
                        'game_calls':gameCalls,
                        'basic_stat_calls':basicStatCalls,
                        'advanced_stat_calls':advancedStatCalls
                    }
                }
            )

        

# client = pymongo.MongoClient("mongodb+srv://nick:{}@cluster0.yhf0e.mongodb.net/UYA-Bot?retryWrites=true&w=majority".format(mongoPW))
# print(client.list_database_names())
# db = client['uya-bot']
# collection = db['time-played']







      



