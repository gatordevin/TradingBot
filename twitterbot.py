import tweepy
import configparser
from datetime import datetime
from dateutil import tz
config = configparser.ConfigParser(interpolation=None)
config.read('twitterkeys.ini')

api_key = config["twitter"]["APIKey"]
api_key_secret = config["twitter"]["APIKeySecret"]
bearer_token = config["twitter"]["BearerToken"]
access_token = config["twitter"]["AccessToken"]
access_token_secret = config["twitter"]["AccessTokenSecret"]

auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
client = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_key_secret, access_token=access_token, access_token_secret=access_token_secret)
api = tweepy.API(auth)

today = datetime.now()
today = today.replace(hour=7, minute=30)
tweets = client.get_users_tweets(id=3690023483, exclude="replies", start_time=today)

for tweet in tweets.data:
    print(tweet)
