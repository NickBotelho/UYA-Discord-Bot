def getSmokers(smokers):
    smokeLine = "None" if len(smokers) == 0 else "People who want to smoke:\n"
    for person in smokers:
        smokeLine+=person+"\n"
    return smokeLine

def pingSmokers(smokePing):
    res = ""
    for smoker in smokePing:
        res+=smokePing[smoker].mention
    return res

def checkTime(db, smokeLine,smokePing, time):
    afk = 30 #minutes
    afk_people = []
    for smoker in smokeLine:
        startTime = smokeLine[smoker]
        if abs((time - startTime )/ 60) > afk:
            afk_people.append(smoker) 
    for person in afk_people:
        del smokeLine[person]
        del smokePing[person]
        db.deleteSmoker(person)
    return smokeLine