from typing_extensions import Self
from Authenticator import Authenticator
from Authenticator import TwitterAuthenticator
import tweepy
from datetime import datetime
from dateutil import tz
from threading import Thread

class TwitterMessage:
    def __init__(self, tweet_data):
        self.__tweet_data = tweet_data
        self.id = self.__tweet_data.id
        self.author_id = tweet_data.author_id
        self.text = self.__tweet_data.text
        self.created = self.__tweet_data.created_at.astimezone(tz.gettz('America/New_York'))
        self.time = datetime.now()

    def __str__(self) -> str:
        print_string = "Twitter Message:\n"
        print_string += f"ID: {self.id}\n"
        print_string += f"Text: {self.text}\n"
        print_string += f"Created At: {self.created}\n"
        print_string += f"Time: {self.time}\n"
        return print_string

class TwitterUser:
    def __init__(self, user_response):
        self.__user_response = user_response
        self.id = self.__user_response.data.id
        self.name = self.__user_response.data.name
        self.time = datetime.now()
        self.messages = []
        self.new_tweets = []
        self.__tweet_listeners : list = []

    def add_tweet_listener(self, listener):
        self.__tweet_listeners.append(listener)

    def is_new_tweets(self):
        return len(self.new_tweets)!=0

    def get_new_tweets(self) -> list[TwitterMessage]:
        temp = self.new_tweets
        self.new_tweets = []
        return temp

    def get_messages(self) -> list[TwitterMessage]:
        return self.messages
    
    def on_tweet(self, tweet : TwitterMessage):
        for message in self.messages:
            message : TwitterMessage
            if message.id == tweet.id:
                return
        print("new twitter message")
        self.messages.append(tweet)
        self.new_tweets.append(tweet)
        for listener in self.__tweet_listeners:
            listener.on_tweet(tweet)
    
    def __str__(self) -> str:
        print_string = "Twitter User:\n"
        print_string += f"ID: {self.id}\n"
        print_string += f"Name: {self.name}"
        return print_string

class TwitterClient(tweepy.StreamingClient):
    twitter_client = None
    def __init__(self):
        self.__auth = TwitterAuthenticator()
        self.__auth_dict = self.__auth.get_twitter_keys()
        self.__client = tweepy.Client(
            bearer_token=self.__auth_dict['bearer_token'], 
            consumer_key=self.__auth_dict['api_key'], 
            consumer_secret=  self.__auth_dict['api_key_secret'], 
            access_token=self.__auth_dict['access_token'], 
            access_token_secret=self.__auth_dict['access_token_secret'], 
            wait_on_rate_limit=True
        )
        super().__init__(self.__auth_dict['bearer_token'])
        self.__users = {}
        self.__twitter_streaming_thread = Thread(target=self.twitter_streaming_main, daemon=True)
        self.__twitter_streaming_thread.start()

        self.__twitter_message_listeners = []
        self.time = datetime.now()

    def twitter_streaming_main(self):
        print("Twitter stream started")
        self.filter(tweet_fields = ["created_at"], expansions=["author_id"], threaded=False  )

    def on_tweet(self, tweet : dict):
        twitter_message : TwitterMessage = TwitterMessage(tweet)
        for listener in self.__twitter_message_listeners:
            listener : TwitterUser
            if listener.id == twitter_message.author_id:
                listener.on_tweet(twitter_message)

    def add_tweet_listener(self, listener : TwitterUser):
        self.__twitter_message_listeners.append(listener)

    def get_tweets(self, user : TwitterUser, start_time : datetime=None, max_results=25):
        if start_time == None:
            start_time = self.time
        if max_results>100:
            tweet_response = tweepy.Paginator(self.__client.get_users_tweets, id=user.id,tweet_fields=["created_at"], expansions=["author_id"], exclude=["replies", "retweets"], start_time=start_time.astimezone(tz.gettz("UTC")), max_results=100).flatten(max_results)
        else:
            tweet_response = tweepy.Paginator(self.__client.get_users_tweets, id=user.id,tweet_fields=["created_at"], expansions=["author_id"], exclude=["replies", "retweets"], start_time=start_time.astimezone(tz.gettz("UTC")), max_results=max_results).flatten(max_results)
        tweet_response = [tweet for tweet in tweet_response]
        tweet_response.reverse()
        for tweet in tweet_response:
            self.on_tweet(tweet)
    
    def get_user(self, handle : str):
        while(True):
            for user in list(self.__users.keys()):
                if user == handle:
                    return self.__users[handle]
            user_response = self.__client.get_user(username=handle)
            try:
                assert user_response.data is not None
                rules = self.get_rules().data
                rule_present = False
                for rule in rules:
                    if handle in rule.value:
                        rule_present = True
                if not rule_present:
                    self.add_rules(tweepy.StreamRule("lang:en -is:retweet -is:reply from:"+handle))
                twitter_user : TwitterUser = TwitterUser(user_response)
                self.add_tweet_listener(twitter_user)
                self.__users[handle] = twitter_user
                return twitter_user
            except AssertionError:
                print("No User found with that handle")
                handle = input("Different Handle: ")
    
    @staticmethod
    def get_client():
        if not TwitterClient.twitter_client:
            TwitterClient.twitter_client = TwitterClient()
        return TwitterClient.twitter_client
