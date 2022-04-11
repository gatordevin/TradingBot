from threading import Thread
from Authenticator import TwitterAuthenticator
import tweepy
from datetime import datetime
from datetime import datetime, tzinfo
from dateutil import tz

class TwitterMessage:
    def __init__(self, tweet_data):
        self.__tweet_data = tweet_data
        print(self.__tweet_data)
        self.id = self.__tweet_data.id
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

    def is_new_tweets(self):
        return len(self.new_tweets)!=0

    def get_new_tweets(self) -> list[TwitterMessage]:
        temp = self.new_tweets
        self.new_tweets = []
        return temp
    
    def on_tweet(self, tweet : TwitterMessage):
        for message in self.messages:
            message : TwitterMessage
            if message.id == tweet.id:
                break
        self.messages.append(tweet)
        self.new_tweets.append(tweet)
    
    def __str__(self) -> str:
        print_string = "Twitter User:\n"
        print_string += f"ID: {self.id}\n"
        print_string += f"Name: {self.name}"
        return print_string
        
class Twitter(tweepy.StreamingClient):
    def __init__(self, twitter_credential_path : str = "config/twitter_credentials.json"):
        self.__twitter_credential_path = twitter_credential_path
        self.__auth = TwitterAuthenticator(self.__twitter_credential_path)
        self.__auth_dict = self.__auth.get_twitter_keys()
        self.__client = tweepy.Client(
            bearer_token=self.__auth_dict['bearer_token'], 
            consumer_key=self.__auth_dict['api_key'], 
            consumer_secret=  self.__auth_dict['api_key_secret'], 
            access_token=self.__auth_dict['access_token'], 
            access_token_secret=self.__auth_dict['access_token_secret']
        )
        super().__init__(self.__auth_dict['bearer_token'])
        self.tweet_listeners = []
        rules = self.get_rules().data
        if rules is not None:
            for rule in self.get_rules().data:
                self.delete_rules(rule.id)
        thread = Thread(target=self.filter, kwargs={"tweet_fields":["created_at"]})
        thread.daemon = True
        thread.start()

    def tweet_listener(self, listener):
        self.tweet_listeners.append(listener)
    
    def on_tweet(self, tweet):
        message = TwitterMessage(tweet)
        for listener in self.tweet_listeners:
            listener : TwitterUser
            listener.on_tweet(message)

    def get_user(self, handle) -> TwitterUser:
        user_response = self.__client.get_user(username=handle)
        self.add_rules(tweepy.StreamRule("lang:en -is:retweet -is:reply from:"+handle))
        twitter_user = TwitterUser(user_response)
        return twitter_user

    def get_user_messages(self, user : TwitterUser, start_time : datetime=None, max_results=25) -> list[TwitterMessage]:
        if start_time == None:
            start_time = self.time
        if max_results>100:
            tweet_response = tweepy.Paginator(self.__client.get_users_tweets, id=user.id,tweet_fields=["created_at"], exclude=["replies", "retweets"], start_time=start_time.astimezone(tz.gettz("UTC")), max_results=100).flatten(max_results)
        else:
            tweet_response = tweepy.Paginator(self.__client.get_users_tweets, id=user.id,tweet_fields=["created_at"], exclude=["replies", "retweets"], start_time=start_time.astimezone(tz.gettz("UTC")), max_results=max_results).flatten(max_results)
        if not tweet_response:
            tweet_response = []
        tweet_response.reverse()
        for response in tweet_response:
            message = TwitterMessage(response)
            user.on_tweet(message)
            for listener in self.tweet_listeners:
                listener : TwitterUser
                listener.on_tweet(message)
        return user.messages
