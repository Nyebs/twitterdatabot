import tweepy
from textblob import TextBlob
from bs4 import BeautifulSoup
import math
import operator
import time
import datetime
import urllib.request
import os
import csv
import progressbar
import numpy as np
from sklearn.svm import SVR
from chatterbot import ChatBot

consumer_key = 'KYhDmj2YaforxBbuK9RfqmBIb'
consumer_secret = 'PqtjyTdMI0PVhj31yBfLMPlJoBHX1sRQ5H5KjoKGeZoZ8WXdFE'
access_token = '854736775960571906-yQlAbv5ATNZoT6sFYkX9pd0SmnILg7H'
access_token_secret = 'qPW2rTP3blpljQBEkhLoHBP7JCtDIbBwIBHSKBtN4TUcx'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#global verbose
#verbose = input("verbose? (y/n): \n> ")

global i
i = 0

chatbot = ChatBot("lain", trainer="chatterbot.trainers.ChatterBotCorpusTrainer")
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")

def folderMaker():
    theDate = time.strftime("%d_%m_%Y")
    if not os.path.exists(theDate):
        os.makedirs(theDate)
        os.chdir(theDate)
    else:
        os.chdir(theDate)
    if function == "1":
        if not os.path.exists("custom"):
            os.makedirs("custom")
            os.chdir("custom")
        else:
            os.chdir("custom")
def getSentiment(api, key):
    public_tweets = api.search(key, count = 100, lang = "en")
    noOfTweets = len(public_tweets)
    totalSentiment = 0
    print("'"+key+"'"+"resulted in:")
    print("\n")
    theTime = time.strftime("%H_%M_%S")
    with open(key + "-" + theTime + ".csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['index', 'author', 'tweet', 'label', 'polarity', 'nouns'])
        global index
        index = int(0)
        for tweet in public_tweets:
            index += 1
            global author
            author = tweet.author._json['screen_name']
            global text
            rawText = tweet.text
            rawText2 = ' '.join([word for word in rawText.split(' ') if len(word) > 0 and word[0] != '@' and word[0] != '#' and 'http' not in word and word != 'RT'])
            rawText3 = rawText2.replace(',', '')
            rawText4 = rawText3.replace(';', '')
            rawText5 = rawText4.replace('&amp', '')
            text = rawText5.replace('\n', '')
            global analysis
            analysis = TextBlob(text)
            global nouns
            nouns = analysis.noun_phrases
            theSentiment = analysis.sentiment.polarity
            if theSentiment == 0:
                noOfTweets -=1
            totalSentiment += theSentiment
            global avgSentiment
            avgSentiment = totalSentiment / noOfTweets
#            if verbose == "y":
#            print("> @" + author + ":", text, " | ", analysis.sentiment)
#            print("\n")
            row_to_add = str(index) + ',' + "@" + author + ',' + text + ','
            if theSentiment > 0:
                file.write(row_to_add + 'Positive' + ',' + str(theSentiment) + ',' + str(nouns))
                file.write('\n')
            elif theSentiment == 0:
                file.write(row_to_add + 'Neutral' + ',' + str(theSentiment) + ',' + str(nouns))
                file.write('\n')
            else:
                file.write(row_to_add + 'Negative' + ',' + str(theSentiment) + ',' + str(nouns))
                file.write('\n')

#    def addMoreEntries():
#        moreEntries = input("more terms? (y/n): \n> ")
#        if moreEntries == "y":
#            key = input("search term?: \n> ")
#            verbose = input("verbose? (y/n): \n> ")
#            longform = input("rerun every 15m? (y/n): \n> ")
#            addMoreEntries()
#            getSentiment(api, key)

def urlGetter():
    url = urllib.request.urlopen("http://www.google.com/trends/hottrends/atom/feed").read().decode("utf-8")
    soup = BeautifulSoup(url, features="xml")
    title = []
    for element in soup.find_all('title'):
        if element.string == "Hot Trends":
            continue
        title.append(element.string)

    views = []
    for element in soup.find_all('approx_traffic'):
        view = element.string.replace(',','')
        view = view.strip('+')
        views.append(int(view))

    q = 0
    trends = dict()
    for element in title:
        trends[element] = views[i]
        q += 1

    sentiments = []
    for preKey in title:
        key = preKey.replace("/", " ")
        thoughts = chatbot.get_response("what do you think about " + key)
        print(thoughts)
        getSentiment(api, key)

def longformChooser():
    global longform
    longform = input("rerun every 15 minutes? [y/n]\n ")

def longformsRevenge():
    if longform == "y":
        try:
            while True:
                print("waiting 15m, press [ctrl]+[c] to quit..")
                bar = progressbar.ProgressBar()
                for i in bar(range(905)):
                    time.sleep(1)
                urlGetter()
        except KeyboardInterrupt:
            print("\n")
            print("average sentiment: " + str(avgSentiment))
            if -1 <= avgSentiment <= -.5:
                print("twitter hates "+key)
            elif -.499999 <= avgSentiment <= -.000001:
                print("twitter dislikes "+key)
            elif avgSentiment == 0:
                print("twitter is neutral about "+key)
            elif .000001 <= avgSentiment <= .5:
                print("twitter likes "+key)
            elif .500001 <= avgSentiment <= 1:
                print("twitter loves "+key)

    elif longform == "n":
        print("\n")
        print("average sentiment: " + str(avgSentiment))
        if -1 <= avgSentiment <= -.5:
            print("twitter hates "+key)
        elif -.499999 <= avgSentiment <= -.000001:
            print("twitter dislikes "+key)
        elif avgSentiment == 0:
            print("twitter is neutral about "+key)
        elif .000001 <= avgSentiment <= .5:
            print("twitter likes "+key)
        elif .500001 <= avgSentiment <= 1:
            print("twitter loves "+key)

global function
function = input("[1]pick a topic or [2]today's topics?\n> ")
if function == "1":
    key = input("> ")
    longformChooser()
    folderMaker()
    getSentiment(api, key)
    longformsRevenge
elif function == "2":
    longformChooser()
    folderMaker()
    urlGetter()
    longformsRevenge
