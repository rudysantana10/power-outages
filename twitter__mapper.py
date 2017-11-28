"""
The following script plots tweets stored in the database. The user has the option of plotting tweets with one of three options:
Group: The user plots clusters of tweets that are within X distance of each other and within a Y timeframe, both X and Y are
        variables passed in by the user
Real-Time: The user plots tweets from the current day onward. This streams for tweets in real-time. Everytime a new tweet is
        caught/found, it is stored in the database. After every 10 minutes, the map is refreshed including all previous and
        newly collected tweets.
Day-to-Day: The user plots all the tweets from given start to end date.
"""

import sys
import math
import time
import json
import couchdb
import webbrowser
from tweepy.streaming import StreamListener
from string import punctuation
from gmplot import GoogleMapPlotter
from the_tweet__stream import listener

server = couchdb.Server('http://localhost:5984')
DB = server['dataset']
tweetMap = 'file:///Users/rodolfosantana7/Desktop/Mining-the-Social-Web-master/python_code/' + 'mymap.html'
startFound = False
po_lat = []
po_lon = []
pl_lat = []
pl_lon = []


def get_dimmensions(tweet):
    bounding_box = DB[tweet]['place']['bounding_box']['coordinates'][0]
    box_coordinates = [(),()]
    box_coordinates[0] = (bounding_box[0][1],bounding_box[1][1],bounding_box[2][1],bounding_box[3][1])
    box_coordinates[1] = (bounding_box[0][0],bounding_box[1][0],bounding_box[2][0],bounding_box[3][0])
    return box_coordinates

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

def timeConvert(hours, minutes):
    totalMinutes = hours * 60
    totalMinutes = totalMinutes + minutes
    return totalMinutes

def inTimeFrame(frame, minutes1, minutes2):
    timeFrame = frame
    timeDist = int(minutes1) - int(minutes2)
    timeDist = abs(timeDist)
    if timeDist > timeFrame:
        return False
    return True
    
def distance(miles, origin, destination):    
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    miles = float(miles)
    maxDist = miles * 1.60934
    if d <= maxDist:
        return True
    return False

def drawGroupBox(group,graph):
    box_coordinates = [(),()]
    lat = []
    log = []
    for tweet in group:
        if DB[tweet]['coordinates'] != None:
            lat.append(DB[tweet]['coordinates']['coordinates'][1])
            log.append(DB[tweet]['coordinates']['coordinates'][0])
        elif DB[tweet]['place']['place_type'] == 'poi':
            lat.append(DB[tweet]['place']['bounding_box']['coordinates'][0][0][1])
            log.append(DB[tweet]['place']['bounding_box']['coordinates'][0][0][0])
    minLat = min(lat)
    maxLat = max(lat)
    minLong = min(log)
    maxLong = max(log)
    box_coordinates[0] = (minLat,minLat,maxLat,maxLat)
    box_coordinates[1] = (minLong,maxLong,maxLong,minLong)
    graph.polygon(box_coordinates[0], box_coordinates[1], edge_color="red", edge_width=3, face_color="red", face_alpha=0.1)


def handle_place(tweet,place,category):
    if DB[tweet]['coordinates'] != None:
        longitude = DB[tweet]['coordinates']['coordinates'][0]
        latitude = DB[tweet]['coordinates']['coordinates'][1]
        if category == 'PO':
            po_lon.append(longitude)
            po_lat.append(latitude)
            
        elif category == 'PL':
            pl_lon.append(longitude)
            pl_lat.append(latitude)
        
    elif place == 'poi':
        longitude = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][0])
        latitude = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][1])
        if (category == 'PO'):
            po_lon.append(longitude)
            po_lat.append(latitude)
            
        elif category == 'PL':
            pl_lon.append(longitude)
            pl_lat.append(latitude)
    
print "*****************************************************************************"
print ""
print "The following system plots tweets according to the option selected by you the user. The options are the following:"
print "Group: Type 'group' to plot clusters of tweets that are within X distance of each other and within a Y timeframe."
print "Real-Time: Type 'real' to plot tweets from the current day onward. This streams for tweets in real-time. After every 10 minutes, the map is refreshed."
print "Day-to-Day: Type 'day' to plot all the tweets from given start to end date."
print ""
print "*****************************************************************************"

searchType = raw_input('Select the type of plotting you would like: ')
city = raw_input('Type central location of search(city or US): ')

if searchType == 'group':
    hours = raw_input('Number of hours tweets may be tweeted from one another: ')
    minutes = raw_input('Number of minutes tweets may be tweeted from one nother: ')
    miles = raw_input('Maximum distance between tweets precise location(mls): ')                 
    ultralist = []
    foundDate = False
    timeFrame = timeConvert(hours, minutes)
    
    for entry in DB:
        closeTweets = []
        currentTweet = DB.get(entry)
        
        if currentTweet['classification'] != 'NP':
            for tweet in DB:
                if sameDate(currentTweet, tweet):
                    foundDate = True
                    while foundDate:
                        currentTime = getTimeCurrent(currentTweet)
                        tweetTime = getTimeTweet(tweet)
                        
                        if inTimeFrame(timeFrame,currentTime,tweetTime):
                            if currentTweet['coordinates'] != None:
                                lat1 = currentTweet['coordinates']['coordinates'][1]
                                long1 = currentTweet['coordinates']['coordinates'][0]
                                if DB[tweet]['coordinates'] != None:
                                    lat2 = DB[tweet]['coordinates']['coordinates'][1]
                                    long2 = DB[tweet]['coordinates']['coordinates'][0]
                                    if distance(miles,(lat1,long1),(lat2,long2)):
                                        closeTweets.append(tweet)
                                elif DB[tweet]['place']['place_type'] == 'poi':
                                    lat2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][1]
                                    long2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][0]
                                    if distance(miles,(lat1,long1),(lat2,long2)):
                                        closeTweets.append(tweet)

                            elif currentTweet['place']['place_type'] == 'poi':
                                lat1 = currentTweet['place']['bounding_box']['coordinates'][0][0][1]
                                long1 = currentTweet['place']['bounding_box']['coordinates'][0][0][0]
                                if DB[tweet]['coordinates'] != None:
                                    lat2 = DB[tweet]['coordinates']['coordinates'][1]
                                    long2 = DB[tweet]['coordinates']['coordinates'][0]
                                    if distance(miles,(lat1,long1),(lat2,long2)):
                                       closeTweets.append(currentTweet)
                                elif DB[tweet]['place']['place_type'] == 'poi':
                                    lat2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][1]
                                    long2 = DB[tweet]['place']['bounding_box']['coordinates'][0][0][0]
                                    if distance(miles,(lat1,long1),(lat2,long2)):
                                       closeTweets.append(tweet)
                        foundDate = False


        density = len(closeTweets)
        if density > 1:
            if closeTweets not in ultralist:
                ultralist.append(closeTweets)
                
    for group in ultralist:
        for tweet in group:
            category = DB[tweet]['classification']
            if DB[tweet]['coordinates'] != None:
                longitude = DB[tweet]['coordinates']['coordinates'][0]
                latitude = DB[tweet]['coordinates']['coordinates'][1]
                if category == 'PO':
                    po_lon.append(longitude)
                    po_lat.append(latitude)
                elif category == 'PL':
                    pl_lon.append(longitude)
                    pl_lat.append(latitude)

            elif DB[tweet]['place']['place_type'] == 'poi':
                longitude = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][0])
                latitude = float(DB[tweet]['place'][u'bounding_box'][u'coordinates'][0][0][1])
                if (category == 'PO'):
                    po_lon.append(longitude)
                    po_lat.append(latitude)
                elif category == 'PL':
                    pl_lon.append(longitude)
                    pl_lat.append(latitude)

    po_scatter_path = (po_lat,po_lon)
    pl_scatter_path = (pl_lat,pl_lon)

    if (city is 'US'):
        mymap = GoogleMapPlotter(39.908213, -99.675441, 4)
    else:
        mymap = GoogleMapPlotter.from_geocode(city, 12)
        lat, lng = mymap.geocode(city)
    for group in ultralist:
        drawGroupBox(group,mymap)
        
    mymap.scatter(po_scatter_path[0], po_scatter_path[1], c='tomato', marker=True)
    mymap.scatter(pl_scatter_path[0], pl_scatter_path[1], c='lemonchiffon', marker=True)
    mymap.draw('./mymap.html')
    webbrowser.open(tweetMap)
        
    
if (searchType == 'real'):
    startDate = raw_input('Enter todays date: ')

    while True:
        for tweet in DB:
            date = DB[tweet][u'created_at']
            place = DB[tweet]['place']['place_type']
            category = DB[tweet]['classification']

            if (startDate in date):
                startFound = True
            if (startFound):
                handle_place(tweet,place,category)

        po_scatter_path = (po_lat,po_lon)
        pl_scatter_path = (pl_lat,pl_lon)
        
        if (city is 'US'):
            mymap = GoogleMapPlotter(39.908213, -99.675441, 4)
        else:
            mymap = GoogleMapPlotter.from_geocode(city, 12)
            lat, lng = mymap.geocode(city)
            ## CIRCLE IMPLEMENTATION
            #mymap.circle(lat, lng, 20000, "#B0C4DE", ew=2)

        ## GRID IMPLEMENTATION
        #mymap.grid(37.42, 37.43, 0.001, -122.15, -122.14, 0.001)
            
        ## HEAT MAP IMPLEMENTATION
        mymap.heatmap(po_scatter_path[0], po_scatter_path[1], threshold=10, radius=40)
        mymap.heatmap(pl_scatter_path[0], pl_scatter_path[1], threshold=10, radius=40)

        mymap.scatter(po_scatter_path[0], po_scatter_path[1], c='tomato', marker=True)
        mymap.scatter(pl_scatter_path[0], pl_scatter_path[1], c='lemonchiffon', marker=True)
        mymap.draw('./mymap.html')
        webbrowser.open(tweetMap)

        liveFeed = listener(StreamListener)
        liveFeed.stream()
        time.sleep(10 * 60)
       

if (searchType == 'day'):
    startDate = raw_input('Start Date: ')
    endDate = raw_input('End Date: ')

    for tweet in DB:
        date = DB[tweet][u'created_at']
        place = DB[tweet]['place']['place_type']
        category = DB[tweet]['classification']

        if (startDate == endDate):
            if (startDate in date):
                handle_place(tweet,place,category)
        else:
            if (startDate in date):
                startFound = True
                handle_place(tweet,place,category)
            elif (endDate in date):
                startFound = False
                handle_place(tweet,place,category)
            elif startFound:
                handle_place(tweet,place,category)

    po_scatter_path = (po_lat,po_lon)
    pl_scatter_path = (pl_lat,pl_lon)
    
    if (city is 'US'):
        mymap = GoogleMapPlotter(39.908213, -99.675441, 4)
    else:
        mymap = GoogleMapPlotter.from_geocode(city, 12)
        lat, lng = mymap.geocode(city)
        ## CIRCLE IMPLEMENTATION
        #mymap.circle(lat, lng, 20000, "#B0C4DE", ew=2)
            
    ## GRID IMPLEMENTATION
    #mymap.grid(37.42, 37.43, 0.001, -122.15, -122.14, 0.001)
        
    ## HEAT MAP IMPLEMENTATION
    mymap.heatmap(po_scatter_path[0], po_scatter_path[1], threshold=10, radius=40)
    mymap.heatmap(pl_scatter_path[0], pl_scatter_path[1], threshold=10, radius=40)
    mymap.scatter(po_scatter_path[0], po_scatter_path[1], c='tomato', marker=True)
    mymap.scatter(pl_scatter_path[0], pl_scatter_path[1], c='lemonchiffon', marker=True)        
    mymap.draw('./mymap.html')
    webbrowser.open(tweetMap)
