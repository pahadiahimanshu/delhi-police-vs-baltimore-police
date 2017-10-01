# 
# Getting replies to the particular handle
# auth - pahadiahimanshu
# 

# TODO - ADD COMMENTS
# Note - I've used bostonpolice multiple times because I checked between the three
from __future__ import division
import time
import json
from datetime import datetime
from pymongo import MongoClient
import matplotlib.pyplot as plt
import re
import tweepy
import operator


username = 'bostonpolice'
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


api = tweepy.API(auth)
# Used nltk corpus to get stop words
stop_words = []

# Top ten users to whose tweets the police station handle retweeted 
# Get their profile description to infer who they are

def toptenretweeted():
    client = MongoClient('localhost', 27017)
    db = client.twitterdb
    delhipolice = db.delhipolice.find()
    bostonpolice = db.bostonpolice.find()
    baltimorepolice = db.baltimorepolice.find()

    mentioneddelhi = db.mentiondelhi.find()
    mentionedbaltimore = db.mentionbaltimore.find()
    # Dictonary to store users and number of retweets
    userdict = {}
    max = -1
    # Get delhi police tweets from db
    for tweet in delhipolice:
        # If the tweet is retweeted
        if 'retweeted_status' in tweet:
            # Get the list of mentioned users
            users =  tweet['entities']['user_mentions']
            for user in users:
                # Get their screen name
                name = user['screen_name']
                # Filter out own retweeted tweets
                if name != 'DelhiPolice':
                    if name not in userdict:
                        userdict[name] = 0
                    userdict[name] +=1
                    if userdict[name] > max:
                        max = userdict[name]
    
    print 'max = ',max
    # Sort the users on the basis of number of retweets by the police handle
    newdict = sorted(userdict.items(), key=operator.itemgetter(1))
    count = 1
    topten = []
    # Decreasing order
    for a in reversed(newdict):
        if count <= 10:
            topten.append(a[0])
        else:
            break
        count += 1
    # now you can call twitter api and see the details
    wordfreq = {}
    # Iterate on the top ten list of users
    for m in topten:
        print m,
        # Get the information about users using the API
        userDetails = api.get_user(m)
        jsondata =  userDetails._json
        # Get description and do word analysis
        description = jsondata['description']
        print description
        splitted = description.split(' ')
        # Remove stop words and special characters and make a word frequency map
        for word in splitted:
            word = re.sub(r'[^\w]', '', word)
            word = re.sub(r"[\x90-\xff]", '', word)
            if word not in stop_words:
                if word not in wordfreq:
                    wordfreq[word] = 0
                wordfreq[word]+=1
    # This is where you know what they do
    for x,y in wordfreq.items():
        print x,y


# Rank the tweets on the basis of content
# eg. see if video is posted, how does it perform (by normalizing)
def entityGraph():
    client = MongoClient('localhost', 27017)
    db = client.twitterdb
    delhipolice = db.delhipolice.find()
    bostonpolice = db.bostonpolice.find()
    baltimorepolice = db.baltimorepolice.find()

    mentioneddelhi = db.mentiondelhi.find()
    mentionedbaltimore = db.mentionbaltimore.find()
    # For graph and score
    videonumberFav = 0
    imagenumberFav = 0
    videonumberRetweet = 0
    imagenumberRetweet = 0
    textnumberFav = 0
    textnumberRetweet = 0

    numvideo = 0
    numimage = 0
    numtext = 0
    policeString = 'Baltimore'
    for tweet in baltimorepolice:
        try:
            if 'media' in tweet['entities']:
                for a in tweet['entities']['media']:
                    # print a['type']
                    url = a['media_url_https']
                    # The media type for video will be photo, so check the url if it contains video
                    if url.find('video') != -1:
                        # print '\tvideo'
                        videonumberFav += tweet['favorite_count']
                        videonumberFav += tweet['retweet_count']
                        numvideo +=1
                    elif a['type']=='photo':
                        # print '\tphoto'
                        imagenumberFav += tweet['favorite_count']
                        imagenumberRetweet += tweet['retweet_count']
                        numimage +=1
            else:
                # All other tweets will be just simple texts
                textnumberFav += tweet['favorite_count']
                textnumberRetweet += tweet['retweet_count']
                numtext +=1
        except Exception,e:
            print '',
    print videonumberFav,videonumberRetweet
    print imagenumberFav, imagenumberRetweet
    print textnumberFav,textnumberRetweet
    # Normalize to get the score
    videoscore =  (videonumberFav+videonumberRetweet)/numvideo
    imagescore =  (imagenumberFav+imagenumberRetweet)/numimage
    textscore =  (textnumberFav+textnumberRetweet)/numtext

    entity = ('video','image','text')
    y_pos = [number for number in xrange(len(entity))]
    allscore = [videoscore, imagescore, textscore]
    # Use matplotlib to plot the scores
    plt.bar(y_pos, allscore, align='center', alpha=0.5)
    plt.xticks(y_pos,entity)
    plt.ylabel('Scores')
    plt.xlabel('Entity')
    plt.title('Popularity of tweet by content')
    plt.savefig(policeString + '_contetnt_popularity.png')


# Give a score to both the twitter handles
# Function mentioned on github repository
def score():
    client = MongoClient('localhost', 27017)
    db = client.twitterdb
    delhipolice = db.delhipolice.find()
    bostonpolice = db.bostonpolice.find()
    baltimorepolice = db.baltimorepolice.find()

    mentioneddelhi = db.mentiondelhi.find()
    mentionedbaltimore = db.mentionbaltimore.find()
    tweetIds =[]
    numberFav = 0
    numberRetweet = 0
    numberReplies = 0
    followers = 1
    friends = 0

    # weights
    weightfav = 4
    weightretweet = 5
    weightreplies = 8
    normalized = 0.0
    scorex =0.0

    for tweet in baltimorepolice:
        numberFav += tweet['favorite_count']
        numberRetweet += tweet['retweet_count']
        followers = tweet['user']['followers_count']
        friends = tweet['user']['friends_count']
        tweetIds.append(tweet['id_str'])

    for replies  in mentionedbaltimore:
        repliedto = replies['in_reply_to_status_id_str']
        # print repliedto,
        if repliedto in tweetIds:
            numberReplies += 1
    print 'fav = ', numberFav
    print 'retweet = ', numberRetweet
    print 'replies = ',numberReplies
    print 'followers = ',followers
    print 'friends = ',friends
    print 'total numbers = ',numberFav+numberReplies+numberRetweet
    scorex = (numberFav * weightfav) + (numberReplies * weightreplies) + (numberRetweet * weightretweet)
    print 'total score = ',scorex

    normalized = scorex/followers
    print 'FINAL = ', normalized*100

# Major concerns in the cities Delhi and Baltimore
# Uses tweets as well as hashtags
def major_concerns():
    global stop_words
    try:
        tweet_words = {}
        tweet_hashtags = {}

        client = MongoClient('localhost', 27017)
        db = client.twitterdb
        delhipolice = db.delhipolice.find()
        bostonpolice = db.bostonpolice.find()
        baltimorepolice = db.baltimorepolice.find()

        for tweet in baltimorepolice:
            text = tweet['text']
            encoding = 'utf-8'
            text = text.encode(encoding)
            text = text.lower()
            
            sentence = text.split(' ')

            # tweet words
            for word in sentence:
                word = re.sub(r'[^\w]', '', word)
                word = re.sub(r"[\x90-\xff]", '', word)
                if word != "" and word.startswith('@') == False and word.startswith('https') == False and len(word)>2:
                    # print type(word),word[0],word[0].isalpha()
                    if word[0].isalpha() == True:
                        if word not in stop_words:
                            if word not in tweet_words:
                                tweet_words[word] = 0
                            tweet_words[word] += 1
            # hashtags
            for m in tweet['entities']['hashtags']:
                # print m['text']
                if m['text'] not in stop_words:
                    if m['text'] not in tweet_hashtags:
                        tweet_hashtags[m['text']] = 0
                    tweet_hashtags[m['text']] +=1
        hashtagnewdict = []
        tweetnewdict = []
        hashtagnewdict = sorted(tweet_hashtags.items(), key=operator.itemgetter(1))
        tweetnewdict = sorted(tweet_words.items(), key=operator.itemgetter(1))
        # print both
        print 'HashTags -------------'
        # for a,b in tweet_hashtags.items():
        #     print a,b
        k=0
        for a in reversed(hashtagnewdict):
            print a[0],a[1]
            k+=1
            if k>=10:
                break
        k = 0
        print 'Tweets ---------------'
        # for a,b in tweet_words.items():
        #     print a,b
        for b in reversed(tweetnewdict):
            print b[0],b[1]
            k+=1
            if k>=10:
                break
    except Exception, e:
        print 'Error',e

# Twitter profile activeness
def freq():
    try:
        tweet_freq = {}
        client = MongoClient('localhost', 27017)
        db = client.twitterdb
        delhipolice = db.delhipolice.find()
        bostonpolice = db.bostonpolice.find()
        baltimorepolice = db.baltimorepolice.find()
        policeString = 'Delhi'
        k =[]
        days = 0
        for tweet in delhipolice:
            date = tweet['created_at'][4:10]

            if date in tweet_freq:
                tweet_freq[date] +=1
            else:
                k.append(date)
                tweet_freq[date] = 0
            # print date
            # print datetime
            # break
        print k
        # sort the dictionary
        newdict = sorted(tweet_freq.items(), key=lambda i: k.index(i[0]))

        # take reverse of that
        x = []
        y = []
        for a in reversed(newdict):
            print a[0],a[1]
            # now put these in different fields
            x.append(a[0])
            y.append(a[1])
        # now just display the frequency bar chart
        xnum = [number for number in xrange(len(newdict))]

        plt.xlabel('Dates')
        plt.ylabel('Number of Tweets')
        plt.title(policeString+' Tweet Frequency')
        plt.xticks(xnum, x, rotation='vertical')
        # Pad margins so that markers don't get clipped by the axes
        # plt.margins(0.2)
        plt.tick_params(axis='x',which='major',pad=15)
        # Tweak spacing to prevent clipping of tick-labels
        plt.subplots_adjust(bottom=0.2)
        plt.plot(xnum,y)
        plt.savefig(policeString+'_activeness.png')
    except Exception,er:
        print er

# Build the stop words list here, add new stop words to this list
def build_stopwords():
    global stop_words
    stop_words = [ 'all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'o', 'hadn', 'herself', 'll', 'had', 'should', 'to', 'only', 'won', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'd', 'did', 'didn', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'hasn', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 're', 'does', 'above', 'between', 'mustn', 't', 'be', 'we', 'who', 'were', 'here', 'shouldn', 'hers', 'by', 'on', 'about', 'couldn', 'of', 'against', 's', 'isn', 'or', 'own', 'into', 'yourself', 'down', 'mightn', 'wasn', 'your', 'from', 'her', 'their', 'aren', 'there', 'been', 'whom', 'too', 'wouldn', 'themselves', 'weren', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'ma', 'these', 'up', 'will', 'below', 'ain', 'can', 'theirs', 'my', 'and', 've', 'then', 'is', 'am', 'it', 'doesn', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'shan', 'needn', 'haven', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'm', 'yours', 'so', 'y', 'the', 'having', 'once','able', 'about', 'above', 'abroad', 'according', 'accordingly', 'across', 'actually', 'adj', 'after',
                  'afterwards', 'again', 'against', 'ago', 'ahead', 'aint', 'all', 'allow', 'allows', 'almost', 'alone',
                  'along', 'alongside', 'already', 'also', 'although', 'always', 'am', 'amid', 'amidst', 'among',
                  'amongst', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway',
                  'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', 'arent', 'around', 'as',
                  'as', 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'back',
                  'backward', 'backwards', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before',
                  'beforehand', 'begin', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better',
                  'between', 'beyond', 'both', 'brief', 'but', 'by', 'came', 'can', 'cannot', 'cant', 'cant', 'caption',
                  'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'cmon', 'co', 'co.', 'com', 'come',
                  'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains',
                  'corresponding', 'could', 'couldnt', 'course', 'cs', 'currently', 'dare', 'darent', 'definitely',
                  'described', 'despite', 'did', 'didnt', 'different', 'directly', 'do', 'does', 'doesnt', 'doing',
                  'done', 'dont', 'down', 'downwards', 'during', 'each', 'edu', 'eg', 'eight', 'eighty', 'either',
                  'else', 'elsewhere', 'end', 'ending', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever',
                  'evermore', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example',
                  'except', 'fairly', 'far', 'farther', 'few', 'fewer', 'fifth', 'first', 'five', 'followed',
                  'following', 'follows', 'for', 'forever', 'former', 'formerly', 'forth', 'forward', 'found', 'four',
                  'from', 'further', 'furthermore', 'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going',
                  'gone', 'got', 'gotten', 'greetings', 'had', 'hadnt', 'half', 'happens', 'hardly', 'has', 'hasnt',
                  'have', 'havent', 'having', 'he', 'hed', 'hell', 'hello', 'help', 'hence', 'her', 'here', 'hereafter',
                  'hereby', 'herein', 'heres', 'hereupon', 'hers', 'herself', 'hes', 'hi', 'him', 'himself', 'his',
                  'hither', 'hopefully', 'how', 'howbeit', 'however', 'hundred', 'id', 'ie', 'if', 'ignored', 'ill',
                  'im', 'immediate', 'in', 'inasmuch', 'inc', 'inc.', 'indeed', 'indicate', 'indicated', 'indicates',
                  'inner', 'inside', 'insofar', 'instead', 'into', 'inward', 'is', 'isnt', 'it', 'itd', 'itll', 'its',
                  'its', 'itself', 'ive', 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'known', 'knows', 'last',
                  'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'lets', 'like', 'liked',
                  'likely', 'likewise', 'little', 'look', 'looking', 'looks', 'low', 'lower', 'ltd', 'made', 'mainly',
                  'make', 'makes', 'many', 'may', 'maybe', 'maynt', 'me', 'mean', 'meantime', 'meanwhile', 'merely',
                  'might', 'mightnt', 'mine', 'minus', 'miss', 'more', 'moreover', 'most', 'mostly', 'mr', 'mrs',
                  'much', 'must', 'mustnt', 'my', 'myself', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary',
                  'need', 'neednt', 'needs', 'neither', 'never', 'neverf', 'neverless', 'nevertheless', 'new', 'next',
                  'nine', 'ninety', 'no', 'nobody', 'non', 'none', 'nonetheless', 'noone', 'no-one', 'nor', 'normally',
                  'not', 'nothing', 'notwithstanding', 'novel', 'now', 'nowhere', 'obviously', 'of', 'off', 'often',
                  'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'ones', 'only', 'onto', 'opposite', 'or',
                  'other', 'others', 'otherwise', 'ought', 'oughtnt', 'our', 'ours', 'ourselves', 'out', 'outside',
                  'over', 'overall', 'own', 'particular', 'particularly', 'past', 'per', 'perhaps', 'placed', 'please',
                  'plus', 'possible', 'presumably', 'probably', 'provided', 'provides', 'que', 'quite', 'qv', 'rather',
                  'rd', 're', 'really', 'reasonably', 'recent', 'recently', 'regarding', 'regardless', 'regards',
                  'relatively', 'respectively', 'right', 'round', 'said', 'same', 'saw', 'say', 'saying', 'says',
                  'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves',
                  'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'shant', 'she', 'shed',
                  'shell', 'shes', 'should', 'shouldnt', 'since', 'six', 'so', 'some', 'somebody', 'someday', 'somehow',
                  'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry',
                  'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 'take', 'taken',
                  'taking', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'thatll', 'thats',
                  'thats', 'thatve', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there',
                  'thereafter', 'thereby', 'thered', 'therefore', 'therein', 'therell', 'therere', 'theres', 'theres',
                  'thereupon', 'thereve', 'these', 'they', 'theyd', 'theyll', 'theyre', 'theyve', 'thing', 'things',
                  'think', 'third', 'thirty', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through',
                  'throughout', 'thru', 'thus', 'till', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried',
                  'tries', 'truly', 'try', 'trying', 'ts', 'twice', 'two', 'un', 'under', 'underneath', 'undoing',
                  'unfortunately', 'unless', 'unlike', 'unlikely', 'until', 'unto', 'up', 'upon', 'upwards', 'us',
                  'use', 'used', 'useful', 'uses', 'using', 'usually', 'v', 'value', 'various', 'versus', 'very', 'via',
                  'viz', 'vs', 'want', 'wants', 'was', 'wasnt', 'way', 'we', 'wed', 'welcome', 'well', 'well', 'went',
                  'were', 'were', 'werent', 'weve', 'what', 'whatever', 'whatll', 'whats', 'whatve', 'when', 'whence',
                  'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'wheres', 'whereupon', 'wherever',
                  'whether', 'which', 'whichever', 'while', 'whilst', 'whither', 'who', 'whod', 'whoever', 'whole',
                  'wholl', 'whom', 'whomever', 'whos', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within',
                  'without', 'wonder', 'wont', 'would', 'wouldnt', 'yes', 'yet', 'you', 'youd', 'youll', 'your',
                  'youre', 'yours', 'yourself', 'yourselves', 'youve', 'zero','police','station','cpdelhi','DelhiPolice','IndependenceDay','ThrowbackThursday','MyBmore','baltimore']
    # stopwords2 = []

# Main function
def main(select):
    if select == 1:
        freq()
    elif select == 2:
        major_concerns()
    elif select == 3:
        score()
    elif select == 4:
        entityGraph()
    elif select == 5:
        toptenretweeted()


build_stopwords()
# Change parameter to access different functions
main(2)