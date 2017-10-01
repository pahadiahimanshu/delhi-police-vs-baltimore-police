# 
# Tweet Scraping for police station handles
# auth - pahadiahimanshu
# 
import time
import tweepy
import json
from datetime import datetime
from pymongo import MongoClient

# Change police handle here baltimorepolice or delhipolice
username = 'baltimorepolice'

# Add your twitter apps credentials here
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Give tweepy access
api = tweepy.API(auth)

# This will get most recent timeline tweets 
user_tweets = api.user_timeline

user = api.get_user(username)
tweets = []

# Get cursor head
tweetHead = tweepy.Cursor(api.user_timeline,id=username, lang='en').items()
count = 0

# Get timeline tweets within the following interval
pastdate = datetime(2017,8,1)
recentdate = datetime(2017,9,8)
loop = True

while loop:
    try:
        # Storing tweets in MongoDB
        client = MongoClient('localhost', 27017)
        # Open twitter db 
        db = client.twitterdb
        # Iterate on head and get next tweets
        tweet = tweetHead.next()
        date = tweet.created_at
        # create another variable with required fields
        # print date

        if date > pastdate and date < recentdate:
            count += 1
            print count

            # get the json field from tweet into a dict
            datajson = tweet._json

            # inside the Twitterdb open baltimorepolice or delhipolice collection
            db.baltimorepolice.insert(datajson)
            tweets.append(tweet)

        elif date < pastdate:
            # Once the date goest past the lower limit, stop the loop
            loop = False
    except tweepy.TweepError, e:
        print 'failed - ',e
        # If rate limit exceeds, sleep for 15 mins (15*60 secs)
        time.sleep(60 * 15)
        continue
    except StopIteration:
        print "Stop iteration?"
        break

count = 1
for tweet in tweets:
    print count, tweet.created_at, tweet.text
    # print tweet
    # print tweet.user
    count+=1
print "done"