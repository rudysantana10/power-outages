"""
Following script includes a number of methods used for filtering out data that is not useful within your couchDB database.
Needed: db - database
"""

import json
import couchdb
from string import punctuation
from twitter__clasifier import classifier

server = couchdb.Server('http://localhost:5984')
db = server['dataset']


# Filters out tweets that are not in the US
def cleanUS():
    for tweet in db:
        if db[tweet]['place']['country'] != "United States":
            del db[tweet]


# Filter out tweets that do not contain terms searched for
def cleanTerm():
    for tweet in db:
        text = db[data]['text']
        text = tweet.lower()
        if ('power outage'not in text) and ('power cut'not in text) and ('power failure'not in text) and ('power blackout'not in text) and ('powers out'not in text) and ('no electricity'not in text) and ('flickering'not in text):
            del db[data]


# Shows the number of tweets pertaining to each respective category
def classifierCount():
    NPs = 0
    PLs = 0
    POs = 0
    for data in db:
        category = db[data]['classification']
        if category == 'NP':
            NPs = NPs + 1
        elif category == 'PL':
            PLs = PLs + 1
        else:
            POs = POs + 1

    print "Number of NP's = " + str(NPs)
    print "Number of PL's = " + str(PLs)
    print "Number of PO's = " + str(POs)
