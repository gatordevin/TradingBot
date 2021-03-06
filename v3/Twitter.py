from email import message
from http.client import responses
from urllib import response
from Authenticator import TwitterAuthenticator
import tweepy
from datetime import datetime, tzinfo
from dateutil import tz

class TwitterUser:
    def __init__(self, user_response):
        self.__user_response = user_response
        self.id = self.__user_response.data.id
        self.name = self.__user_response.data.name
        self.time = datetime.now()

    def __str__(self) -> str:
        print_string = "Twitter User:\n"
        print_string += f"ID: {self.id}\n"
        print_string += f"Name: {self.name}"
        return print_string
    
class TwitterMessage:
    def __init__(self, tweet_data):
        self.__tweet_data = tweet_data
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


class Twitter:
    def __init__(self, auth_file="config/twitter_credentials.json"):
        self.__authenticator = TwitterAuthenticator(auth_file)
        self.__auth_dict = self.__authenticator.get_twitter_keys()
        self.__client = tweepy.Client(
            bearer_token=self.__auth_dict['bearer_token'], 
            consumer_key=self.__auth_dict['api_key'], 
            consumer_secret=  self.__auth_dict['api_key_secret'], 
            access_token=self.__auth_dict['access_token'], 
            access_token_secret=self.__auth_dict['access_token_secret']
        )
        self.time = datetime.utcnow()

    def get_user(self, handle) -> TwitterUser:
        user_response = self.__client.get_user(username=handle)
        twitter_user = TwitterUser(user_response)
        return twitter_user

    def get_user_messages(self, user : TwitterUser, start_time : datetime=None, max_results=25) -> list[TwitterMessage]:
        if start_time == None:
            start_time = self.time
        if max_results>100:
            tweet_response = tweepy.Paginator(self.__client.get_users_tweets, id=user.id,tweet_fields=["created_at"], exclude=["replies", "retweets"], start_time=start_time.astimezone(tz.gettz("UTC")), max_results=100).flatten(max_results)
        else:
            tweet_response = tweepy.Paginator(self.__client.get_users_tweets, id=user.id,tweet_fields=["created_at"], exclude=["replies", "retweets"], start_time=start_time.astimezone(tz.gettz("UTC")), max_results=max_results).flatten(max_results)
        # print(tweet_response)
        # for tweet in tweet_response:
        #     print(tweet)
        # tweet_response = self.__client.get_users_tweets()
        # print(tweet_response)
        # tweet_response = tweet_response.data
        if not tweet_response:
            tweet_response = []
        messages = [TwitterMessage(response) for response in tweet_response]
        messages.reverse()
        return messages
            