# -*- coding: utf-8 -*-

import sys
import tweepy
import couchdb
import json
import webbrowser

# Query terms
server = couchdb.Server('http://localhost:5984')
DB = 'database'

# Get these values from your application settings

CONSUMER_KEY = 'fFRVfkuoNyafZglDwDGKpWF1o'
CONSUMER_SECRET = 'lRMw1avbxoKF13eJ0CeF9WYC6jqMga4310mz6O3uyBQdOUDYkC'

# Get these values from the "My Access Token" link located in the
# margin of your application details, or perform the full OAuth
# dance

ACCESS_TOKEN = '978717116-53nmofGg5IrJoCSOaeeHp6eBWBkQFWqtRKtSDeK4'
ACCESS_TOKEN_SECRET = 'DMpeXk04NXoMKeZw6t7VXiOxc2k8vQjwkr8PPYZ79IXJn'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Note: Had you wanted to perform the full OAuth dance instead of using
# an access key and access secret, you could have uses the following 
# four lines of code instead of the previous line that manually set the
# access token via auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# 
# auth_url = auth.get_authorization_url(signin_with_twitter=True)
# webbrowser.open(auth_url)
# verifier = raw_input('PIN: ').strip()
# auth.get_access_token(verifier)

class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        
        # We'll simply print some values in a tab-delimited format
        # suitable for capturing to a flat file but you could opt 
        # store them elsewhere, retweet select statuses, etc.
        data = json.loads(status)

        try:
            db = server.create(DB)
        except couchdb.http.PreconditionFailed, e:
            db = server[DB]
        db.save(data)
        return True

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

# Create a streaming API and set a timeout value of 1 minute
streaming_api = tweepy.streaming.Stream(auth, CustomStreamListener(), timeout=60)

# Optionally filter the statuses you want to track by providing a list
# of users to "follow"

streaming_api.filter(track = ['power outage','power cut','power failure','power blackout', 'powers out', 'no electricity', 'flickering lights'])
