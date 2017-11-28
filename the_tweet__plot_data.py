# -*- coding: utf-8 -*-
"""
Following script provides csv file with information regarding the tweet
csv file can be uploaded into Google Maps in the following link below:
https://www.google.com/maps/d/u/0/edit?mid=zoblGYJKN9EE.kad5hO6qHX_c
"""

import csv
import math
import json
import couchdb


def getDateTweet(tweet):
    date = DB[tweet]['created_at'][4:10]
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
    hour = int(DB[tweet]['created_at'][11:13])
    minute = int(DB[tweet]['created_at'][14:16])
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

def get_Lat(tweet):
    southLat = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][1])
    northLat = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][2][1])
    difference = northLat - southLat
    midDist = difference / 2
    latitude = southLat + midDist
    return latitude

def get_Long(tweet):
    westLong = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][0])
    eastLong = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][2][0])
    difference = westLong - eastLong
    midDist = difference / 2
    longitude = westLong - midDist
    return longitude

#day = raw_input('Enter day for search: ')
#location = raw_input('Select City: ')

server = couchdb.Server('http://localhost:5984')
DB = server['dataset']

with open("plot.csv", "w") as f:
    csv_w = csv.writer(f)
    csv_w.writerow(['Category','Tweet','Type','Date','Location','Longitude','Latitude'])
    ultralist = []
    foundDate = False
    for tweet in DB:
        closeTweets = []
        category = DB[tweet]['classification']

        currentTweet = DB.get(tweet)
        
        if category != 'NP':
            for tweet in DB:
                if sameDate(currentTweet, tweet):
                    foundDate = True
                    while foundDate:
                        currentTime = getTimeCurrent(currentTweet)
                        tweetTime = getTimeTweet(tweet)
                        
                        if inTimeFrame(currentTime,tweetTime):
                            if currentTweet['coordinates'] != None:
                                lat1 = currentTweet['coordinates']['coordinates'][1]
                                long1 = currentTweet['coordinates']['coordinates'][0]
                                if DB[tweet]['coordinates'] != None:
                                    lat2 = DB[tweet]['coordinates']['coordinates'][1]
                                    long2 = DB[tweet]['coordinates']['coordinates'][0]
                                    if distance((lat1,long1),(lat2,long2)):
                                        closeTweets.append(tweet)
                                elif DB[tweet]['place']['place_type'] == 'poi':
                                    lat2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][1]
                                    long2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][0]
                                    if distance((lat1,long1),(lat2,long2)):
                                        closeTweets.append(tweet)

                            elif currentTweet['place']['place_type'] == 'poi':
                                lat1 = currentTweet['place']['bounding_box']['coordinates'][0][0][1]
                                long1 = currentTweet['place']['bounding_box']['coordinates'][0][0][0]
                                if DB[tweet]['coordinates'] != None:
                                    lat2 = DB[tweet]['coordinates']['coordinates'][1]
                                    long2 = DB[tweet]['coordinates']['coordinates'][0]
                                    if distance((lat1,long1),(lat2,long2)):
                                       closeTweets.append(currentTweet)
                                elif DB[tweet]['place']['place_type'] == 'poi':
                                    lat2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][1]
                                    long2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][0]
                                    if distance((lat1,long1),(lat2,long2)):
                                       closeTweets.append(tweet)
                        foundDate = False


        density = len(closeTweets)
        if density > 1:
            if closeTweets not in ultralist:
                ultralist.append(closeTweets)
    for group in ultralist:
        print group
        print ''
        for tweet in group:
            cat = DB[tweet]['classification']
            category = DB[tweet]['classification']
            print DB[tweet]['user']['screen_name']
            if DB[tweet]['coordinates'] != None:
                text = str(DB[tweet]['_id'])
                date = DB[tweet]['created_at']
                latitude = DB[tweet]['coordinates']['coordinates'][1]
                longitude = DB[tweet]['coordinates']['coordinates'][0]
                place = DB[tweet]['place']['full_name']
                csv_w.writerow([cat,text,category,date,place,longitude,latitude])

            elif DB[tweet]['place']['place_type'] == 'poi':
                text = str(DB[tweet]['_id'])
                date = DB[tweet]['created_at']
                latitude = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][1])
                longitude = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][0])
                place = DB[tweet]['place']['full_name']
                csv_w.writerow([cat,text,category,date,place,longitude,latitude])
    
    print len(ultralist)


f.close()
