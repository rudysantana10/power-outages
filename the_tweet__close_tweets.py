import json
import math
import couchdb


def getDateTweet(tweet):
    date = db[tweet]['created_at'][4:10]
    return date

def getDateCurrent(tweet):
    date = tweet['created_at'][4:10]
    return date

def sameDate(tweet1, tweet2):
    firstDate = getDateCurrent(tweet1)
    secondDate = getDateTweet(tweet2)
    return firstDate == secondDate

def minuteConverter(hour):
    minutes = hour * 60
    return minutes

def getTimeTweet(tweet):
    hour = int(db[tweet]['created_at'][11:13])
    minute = int(db[tweet]['created_at'][14:16])
    minutes = minute + minuteConverter(hour)
    return minutes

def getTimeCurrent(tweet):
    hour = int(tweet['created_at'][11:13])
    minute = int(tweet['created_at'][14:16])
    minutes = minute + minuteConverter(hour)
    return minutes

def inTimeFrame(minutes1, minutes2):
    timeFrame = 3 * 60
    timeDist = int(minutes1) - int(minutes2)
    timeDist = abs(timeDist)
    if timeDist > timeFrame:
        return False
    return True

    
def distance(origin, destination):    
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    if d <= 40.2336:
        return True
    return False


server = couchdb.Server('http://localhost:5984')
db = server['test']
ultralist = []
foundDate = False
count = 0
for entry in db:
    closeTweets = []
    count = count + 1
    print count
    if len(ultralist) > 0:
        for thing in ultralist:
            print "GROUP............................................."
            print thing
            print ''
            print ''

    currentTweet = db.get(entry)
    
    if currentTweet['classification'] != 'NP':
        for tweet in db:
            if sameDate(currentTweet, tweet):
                foundDate = True
                while foundDate:
                    currentTime = getTimeCurrent(currentTweet)
                    tweetTime = getTimeTweet(tweet)
                    
                    if inTimeFrame(currentTime,tweetTime):
                        if currentTweet['coordinates'] != None:
                            lat1 = currentTweet['coordinates']['coordinates'][1]
                            long1 = currentTweet['coordinates']['coordinates'][0]
                            if db[tweet]['coordinates'] != None:
                                lat2 = db[tweet]['coordinates']['coordinates'][1]
                                long2 = db[tweet]['coordinates']['coordinates'][0]
                                if distance((lat1,long1),(lat2,long2)):
                                    closeTweets.append(tweet)
                            elif db[tweet]['place']['place_type'] == 'poi':
                                lat2 = db[tweet]['place']['bounding_box']['coordinates'][0][0][1]
                                long2 = db[tweet]['place']['bounding_box']['coordinates'][0][0][0]
                                if distance((lat1,long1),(lat2,long2)):
                                    closeTweets.append(tweet)

                        elif currentTweet['place']['place_type'] == 'poi':
                            lat1 = currentTweet['place']['bounding_box']['coordinates'][0][0][1]
                            long1 = currentTweet['place']['bounding_box']['coordinates'][0][0][0]
                            if db[tweet]['coordinates'] != None:
                                lat2 = db[tweet]['coordinates']['coordinates'][1]
                                long2 = db[tweet]['coordinates']['coordinates'][0]
                                if distance((lat1,long1),(lat2,long2)):
                                   closeTweets.append(currentTweet)
                            elif db[tweet]['place']['place_type'] == 'poi':
                                lat2 = db[tweet]['place']['bounding_box']['coordinates'][0][0][1]
                                long2 = db[tweet]['place']['bounding_box']['coordinates'][0][0][0]
                                if distance((lat1,long1),(lat2,long2)):
                                   closeTweets.append(tweet)
                    foundDate = False


    density = len(closeTweets)
    if density > 1:
        if closeTweets not in ultralist:
            ultralist.append(closeTweets)

            
for thing in ultralist:
    print "GROUP............................................."
    for tweet in thing:
        print db[tweet]['_id']
        print db[tweet]['text']
        print db[tweet]['created_at']
        print db[tweet]['place']['full_name']
        print ''

    print ''
print len(ultralist)
