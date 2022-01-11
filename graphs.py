import matplotlib.pyplot as plt
from mongodb import Database
import datetime
monthNames = [
    "Jan",'Feb',
    'Mar', 'Apr', 'May', "Jun", 'Jul', 'Aug',
    'Sep', 'Oct', 'Nov', 'Dec'
]
weekdaysNames = [
    'Sun', 'Mon', 'Tue', 'Wed',
    'Thu', 'Fri', 'Sat'
]
def produceGraphs(gameSize = 2):
    plt.rcParams['axes.facecolor'] = '#9B5A06'
    game_history = Database("UYA", "Game_History")
    dates = {}
    months = [0 for i in range(12)]
    weekdays = [0 for i in range(7)]
    for game in game_history.collection.find():
        if len(game['player_ids']) < gameSize: continue
        results = game['game_results']

        date = game['date'] #"Thu, 22 July 2021"
        args = date.split(" ")
        if len(args[2]) > 3: continue
        dates[date] = 1 if date not in dates else dates[date] + 1

        date = datetime.datetime.strptime(date, "%a, %d %b %Y")
        month = date.month
        weekday = date.weekday()

        months[month-1] +=1
        weekdays[weekday]+=1

    plt.clf()
    plt.bar(x = monthNames, height = months, color = '#FFA836')
    plt.title("Games Played By Month {}v{}+".format(gameSize//2,gameSize//2))
    plt.ylabel("Games Played")
    plt.xlabel("Month")
    plt.xticks(rotation = 50)
    plt.tight_layout()
    plt.savefig("graphs/months{}v{}+".format(gameSize//2,gameSize//2))



    plt.clf()
    plt.bar(x = weekdaysNames, height = weekdays, color = '#FFA836')
    plt.title("Games Played By Weekday {}v{}+".format(gameSize//2,gameSize//2))
    plt.ylabel("Games Played")
    plt.xlabel("Weekday")
    plt.xticks(rotation = 50)
    plt.tight_layout()
    plt.savefig("graphs/weekdays{}v{}+".format(gameSize//2,gameSize//2))

def DAU():
    plt.rcParams['axes.facecolor'] = '#9B5A06'
    game_history = Database("UYA", "Game_History")
    dates = {}
    months = [0 for i in range(12)]
    weekdays = [0 for i in range(7)]
    for game in game_history.collection.find():
        results = game['game_results']

        date = game['date'] #"Thu, 22 July 2021"
        if date not in dates:
            dates[date] = set()

        for player in game['player_ids']:
            dates[date].add(player)

    dates = {date:len(dates[date]) for date in dates}
    print(dates)
    plt.clf()
    plt.bar(x = dates.keys(), height = dates.values(), color = '#FFA836')
    plt.title("DAU")
    plt.ylabel("Users")
    plt.xlabel("Date")
    plt.xticks(rotation = 50)
    plt.tight_layout()
    plt.savefig("graphs/DAU")



# produceGraphs(4)
# produceGraphs(6)
# produceGraphs(8)