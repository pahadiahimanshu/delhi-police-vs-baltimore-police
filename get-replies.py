# 
# Getting replies to the particular handle
# auth - pahadiahimanshu
# 
from pymongo import MongoClient
import tweepy
import time
from datetime import datetime

username = 'baltimorepolice'
# Add your twitter apps credentials here
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


api = tweepy.API(auth)

# To get all the tweets wherre baltimorepolice was mentioned
QUERY = "to:baltimorepolice"

pastdate = datetime(2017,8,1)
recentdate = datetime(2017,9,8)
try:
    client = MongoClient('localhost', 27017)
    db = client.twitterdb
    # Get all the tweets from baltimorepolice db (mongodb)
    tweet = db.baltimorepolice.find()
    dict = {}
    count = 0
    cond = True
    # store all mentions since 1 september tweet
    for t in tweet:
        # Get mentions using the query (english only)
        mentions = tweepy.Cursor(api.search, q=QUERY,sinceId=t['id_str'], lang='en').items()
        while cond:
            try:
                t = mentions.next()
                datajson = t._json
                # print datajson['id_str']
                date = t.created_at
                if date > pastdate and date < recentdate:
                    # mention should be between this date only
                    if datajson['in_reply_to_status_id_str'] != None:
                        db.mentionboston.insert(datajson)
                        print date,datajson['user']['screen_name'],datajson['in_reply_to_status_id_str']
                        print datajson['text']

            except tweepy.TweepError, e:
                print 'failed - ', e
                time.sleep(60 * 15)
                continue
            except StopIteration:
                print "Stop iteration?"
                break
        break
    maxx = -1

    for a,b in dict.items():
        if b>=maxx and a!=None:
            maxx = b
            print b
            print a
        # print a,b
    print 'max replied to',maxx
except Exception,e:
    print e
