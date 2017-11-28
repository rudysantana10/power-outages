"""
Following script imports a json file into couchDB. This script pick ut certain traits from a tweet that suits this project.
Make sure you are creating documents that contain the entities that are most suitable for the project.
Needed: db - database
        x.json - json file
"""

import json
import couchdb
from string import punctuation
from twitter__clasifier import classifier

server = couchdb.Server('http://localhost:5984')
db = server['test']


def append():
    db = server['test']

    with open('tweet_search.json') as data_file:
        data = json.load(data_file)
        for thing in data["docs"]:
            if thing["coordinates"] != None:
                tweet =  thing["text"]
                tweet = tweet.lower()
                docID = thing["_id"]
                category = classifier(tweet)

                db[docID] = dict(contributors = thing["contributors"],entities = thing["entities"],favorite_count = thing["favorite_count"],created_at = thing["created_at"], coordinates = thing["coordinates"], place = thing["place"], text = thing["text"], classification = category, user = thing["user"], retweet_count = thing["retweet_count"], retweeted = thing["retweeted"])
                
            elif thing["place"]["place_type"] == "poi":
                tweet =  thing["text"]
                tweet = tweet.lower()
                category = classifier(tweet)
                docID = thing["_id"]

                db[docID] = dict(contributors = thing["contributors"],entities = thing["entities"],favorite_count = thing["favorite_count"],created_at = thing["created_at"], coordinates = thing["coordinates"], place = thing["place"], text = thing["text"], classification = category, user = thing["user"], retweet_count = thing["retweet_count"], retweeted = thing["retweeted"])

append()
