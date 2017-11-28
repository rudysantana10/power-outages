import couchdb
import time
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from string import punctuation
from twitter__clasifier import classifier


ckey = 'fFRVfkuoNyafZglDwDGKpWF1o'
csecret = 'lRMw1avbxoKF13eJ0CeF9WYC6jqMga4310mz6O3uyBQdOUDYkC'
atoken = '978717116-53nmofGg5IrJoCSOaeeHp6eBWBkQFWqtRKtSDeK4'
asecret = 'DMpeXk04NXoMKeZw6t7VXiOxc2k8vQjwkr8PPYZ79IXJn'
server = couchdb.Server('http://localhost:5984')
DB = 'test'

class listener(StreamListener):
    
    def on_data(self, tweet):
        data = json.loads(tweet)

        if (data['place'] != None and data['place']['country'] == "United States"):
            tweet = data['text']
            tweet = tweet.lower()
                

            if ('power outage'in tweet) or ('power cut'in tweet) or ('power failure'in tweet) or ('power blackout'in tweet) or ('powers out'in tweet) or ('no electricity'in tweet) or ('flickering'in tweet):
                data['entities']['symbols'] = classifier(tweet)
                data['_id'] = data['id_str']
                del data['id_str']
                tweetID = data['_id']
                
                try:
                    db = server.create(DB)
                except couchdb.http.PreconditionFailed, e:
                    db = server[DB]
                db.save(data)
                print tweet
                return True


    def on_error(self, status):
        print status


    def stream(self):
        auth = OAuthHandler(ckey,csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track = ['power outage','power cut','power failure','power blackout', 'powers out', 'no electricity', 'flickering lights'], async=True)
