import sys
from Logger import logs
import os
import configparser
import tweepy
import requests
from datetime import datetime, timedelta
from dateutil import tz

class TwitterAPI():
    def __init__(self, keys_file):
        #INIT API KEYS
        logs.debug("Creating twitter API using " + keys_file)
        self.__keys_file = keys_file
        self.__config = configparser.ConfigParser(interpolation=None)
        if not os.path.isfile(self.__keys_file):
            logs.info(keys_file + " does not exist. Requesting keys!")
            os.makedirs(os.path.dirname(self.__keys_file), exist_ok=True)
            self.__api_key = input("API Key: ")
            self.__api_key_secret = input("API Key Secret: ")
            self.__bearer_token = input("Bearer Token: ")
            self.__access_token = input("Access Token: ")
            self.__access_token_secret = input("Access Token Secret: ")
            self.__config.add_section('twitter')
            self.__config['twitter']['APIKey'] = self.__api_key
            self.__config['twitter']['APIKeySecret'] = self.__api_key_secret
            self.__config['twitter']['BearerToken'] = self.__bearer_token
            self.__config['twitter']['AccessToken'] = self.__access_token
            self.__config['twitter']['AccessTokenSecret'] = self.__access_token_secret
            with open(self.__keys_file, 'w') as configfile:
                self.__config.write(configfile)
            logs.info(keys_file + " succesfully created!")
        else:
            self.__config.read(self.__keys_file)
            logs.info(keys_file + " succesfully created!")
        
        #CREATE TWITTER API OBJECTS
        self.__auth = tweepy.OAuth1UserHandler(
            self.__config['twitter']['APIKey'], 
            self.__config['twitter']['APIKeySecret'], 
            self.__config['twitter']['AccessToken'], 
            self.__config['twitter']['AccessTokenSecret'])
        self.client = tweepy.Client(
            bearer_token=self.__config['twitter']['BearerToken'], 
            consumer_key=self.__config['twitter']['APIKey'], 
            consumer_secret=self.__config['twitter']['APIKeySecret'], 
            access_token=self.__config['twitter']['AccessToken'], 
            access_token_secret=self.__config['twitter']['AccessTokenSecret'])
        self.api = tweepy.API(self.__auth)
        logs.debug("Tweepy API Objects created")

    def get_twitter_user(self, handle):
        logs.debug("Getting twitter user information for " + handle)
        twitter_user = TwitterUser(self.client.get_user(username=handle), self)
        logs.debug("Succesfully received twitter information for " + handle)
        return twitter_user

class TwitterUser():
    def __init__(self, get_user_response, twitter_api):
        logs.debug("Creating TwitterUser object")
        self.screen_name = get_user_response.data["username"]
        self.user_id = get_user_response.data["id"]
        self.__twitter_api : TwitterAPI = twitter_api
        self.__tweet_messages = []
        self.__creation_time = datetime.now()

    def get_tweets(self, start_time, only_new):
        twitter_tweet_data = self.__twitter_api.client.get_users_tweets(id=self.user_id,tweet_fields=["created_at"], exclude=["replies", "retweets"], start_time=start_time).data
        if twitter_tweet_data is not None:
            logs.debug("Succesfully got tweets from " + start_time.strftime("%Y-%m-%d"))
            tweet_list = []
            for tweet in twitter_tweet_data:
                current_tweet_message = TweetMessage(tweet, self, self.__twitter_api)
                exists = False
                for tweet_message in self.__tweet_messages:
                    if(tweet_message.id==current_tweet_message.id):
                        exists = True
                if not exists:
                    self.__tweet_messages.append(current_tweet_message)
                    tweet_list.append(current_tweet_message)
                else:
                    if not only_new:
                        tweet_list.append(current_tweet_message)
            tweet_list.reverse()
            return tweet_list
        else:
            return []
    
    def get_daily_tweets(self, day=None, only_new=True):
        if day is None:
            day = datetime.now().date()
        start = datetime(day.year, day.month, day.day).astimezone(tz.gettz("UTC"))
        logs.debug("Requesting tweets from " + day.strftime("%Y-%m-%d"))
        return self.get_tweets(start, only_new)

    def get_live_tweets(self, only_new=True):
        start = self.__creation_time.astimezone(tz.gettz("UTC"))
        logs.debug("Requesting live tweets")
        return self.get_tweets(start, only_new)

class TweetMessage():
    def __init__(self, tweet_result, user, twitter_api):
        logs.debug("Creating TweetMessage object")
        self.__tweet_result = tweet_result
        self.id = self.__tweet_result.data["id"]
        self.text = self.__tweet_result.data["text"]
        self.date = self.__tweet_result.created_at.astimezone(tz.gettz('America/New_York'))
        self.user : TwitterUser = user
        self.__twitter_api : TwitterAPI = twitter_api