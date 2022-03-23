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

class StockEntry():
    def __init__(self, ticker, buy_type, buy_value):
        self.ticker = ticker
        if "c" in buy_type:
            self.buy_type = "call"
        else:
            self.buy_type = "put"
        self.buy_value = buy_value

    def __str__(self):
        return_string = "Ticker: " + self.ticker + "\n"
        return_string += "Option type: " + self.buy_type + "\n"
        return_string += "Option value: " + self.buy_value + "\n"
        return return_string

include_lotto = False
stock_entries = []
for tweet in tweets.data:
    if "entry" in str(tweet):
        if "LOTTO" in str(tweet) and not include_lotto:
            pass
        else:
            words = str(tweet).split(" ")
            ticker = words[1]
            buy_type = words[2][-1]
            buy_value = words[2][:-1]
            stock_entries.append(StockEntry(ticker, buy_type, buy_value))

for entry in stock_entries:
    print(entry)