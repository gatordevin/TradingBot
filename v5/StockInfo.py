from Twitter import TwitterClient, TwitterMessage
from threading import Thread
from datetime import datetime
from time import sleep

class StockInfoSink():
    def __init__(self):
        super().__init__()
        pass

    def on_data_sink(self, data):
        pass

class StockInfoSource():
    def __init__(self):
        super().__init__()
        self.__sinks : list[StockInfoSink] = []

    def add_sink(self, sink : StockInfoSink):
        self.__sinks.append(sink)

    def on_data_source(self, data):
        for sink in self.__sinks:
            sink.on_data_sink(data)

class TwitterUserStockInfo(StockInfoSource):
    def __init__(self, twitter_handle : str, live : bool = True, start_time=datetime.now()):
        super().__init__()
        self.__live = live
        self.__start_time = start_time
        self.__twitter_handle : str = twitter_handle
        self.__twitter_client : TwitterClient = TwitterClient.get_client()
        self.__twitter_user = self.__twitter_client.get_user(self.__twitter_handle)
        self.__twitter_user.add_tweet_listener(self)
        if not self.__live:
            self.__message_thread = Thread(target=self.message_thread_loop, daemon=True)
            self.__message_thread.start()

    def message_thread_loop(self):
        while True:
            self.__twitter_client.get_tweets(self.__twitter_user, start_time=self.__start_time)
            sleep(1)

    def on_tweet(self, tweet : TwitterMessage):
        self.on_data_source(tweet)

    def get_twitter_user(self):
        return self.__twitter_user