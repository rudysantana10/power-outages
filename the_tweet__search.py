# -*- coding: utf-8 -*-

import sys
import twitter
import couchdb
import json
import csv
import time
from couchdb.design import ViewDefinition
from twitter__login import login

#list_of_terms = ['power outage','power cut','power failure','power blackout', 'powers out', 'no electricity', 'flickering lights']
list_of_terms = ['metro boom']
MAX_PAGES = 10

server = couchdb.Server('http://localhost:5984')
DB = server['test']
geotagged = []

for term in list_of_terms:
    t = login()
    search_results = t.search.tweets(q=term, count=1000)
    tweets = search_results['statuses']

    for _ in range(MAX_PAGES-1): # Get more pages
        next_results = search_results['search_metadata']['refresh_url']
        #next_results = search_results['search_metadata']['next_results']

        # Create a dictionary from the query string params
        kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

        search_results = t.search.tweets(**kwargs)
        tweets += search_results['statuses']

        if len(search_results['statuses']) == 0:
            break

### Change couchDB id to tweets id
### Append the entry to geotagged collection
    for tweet in tweets:
        if tweet[u'place'] != None:
            text = tweet['text']
            for term in list_of_terms:
                if term in text:
                    tweet['_id'] = tweet['id_str']
                    del tweet['id_str']
                    geotagged.append(tweet)
                    
# Store the data
try:
    db = server.create(DB)
except couchdb.http.PreconditionFailed, e:
    # Already exists, so append to it (but be mindful of appending duplicates with repeat searches.)
    # The refresh_url in the search_metadata or streaming API might also be
    # appropriate to use here.
    db = server[DB]
db.update(geotagged, all_or_nothing=True)
