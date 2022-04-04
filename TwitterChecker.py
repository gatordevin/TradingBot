from threading import Thread
from time import sleep, monotonic
import tweepy
import configparser
from datetime import date, datetime, timedelta

class TwitterStockChecker():
    def __init__(self, start_time, twitter_user_id, api_keys_path, end_time=None, back_test_speed=60):
        self.__scan_rate = 30
        self.__twitter_user_id = twitter_user_id
        self.__config = configparser.ConfigParser(interpolation=None)
        self.__config.read(api_keys_path)
        self.__start_time = start_time+timedelta(hours=4)
        self.__end_time = end_time
        self.__back_test_speed = back_test_speed
        self.init_twitter_api()
        self.__back_test_time = self.__start_time
        self.__scan_twitter_thread = Thread(target=self.scan_twitter)
        self.__scan_twitter_thread.daemon = True
        self.__scan_twitter_thread.start()
        self.__current_tweets = []
        self.__stock_alerts = []

    def init_twitter_api(self):
        auth = tweepy.OAuth1UserHandler(
            self.__config["twitter"]["APIKey"], 
            self.__config["twitter"]["APIKeySecret"], 
            self.__config["twitter"]["AccessToken"], 
            self.__config["twitter"]["AccessTokenSecret"])
        self.__client = tweepy.Client(
            bearer_token=self.__config["twitter"]["BearerToken"], 
            consumer_key=self.__config["twitter"]["APIKey"], 
            consumer_secret=self.__config["twitter"]["APIKeySecret"], 
            access_token=self.__config["twitter"]["AccessToken"], 
            access_token_secret=self.__config["twitter"]["AccessTokenSecret"])
        # self.__client = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_key_secret, access_token=access_token, access_token_secret=access_token_secret)

        self.__api = tweepy.API(auth)
    
    def scan_twitter(self):
        back_test = False
        if(self.__end_time!=None):
            back_test = self.__end_time < datetime.now()
        scan_end_time = self.__end_time
        program_start_time = monotonic()
        while(True):
            sleep(60/self.__scan_rate)
            if(back_test):
                elapsed_time = monotonic()-program_start_time
                scan_end_time = self.__start_time + timedelta(seconds=elapsed_time*self.__back_test_speed)
                self.__back_test_time = scan_end_time
                if(scan_end_time>self.__end_time):
                    break
            try:
                # print("Pinging Twitter " + str(monotonic()))
                tweets = self.__client.get_users_tweets(id=self.__twitter_user_id, exclude="replies", end_time=scan_end_time,start_time=self.__start_time,max_results=20)
                # print("Twitter Pinged " + str(monotonic()))
                # if(tweets.meta["result_count"]!=0):
                #     print("Got")
                if tweets.data is not None:
                    for tweet in list(tweets.data)[::-1]:
                        if tweet not in self.__current_tweets:
                            if "entry" in str(tweet)[0:5]:
                                words = str(tweet).split(" ")
                                ticker = words[1]
                                buy_type = words[2][-1]
                                buy_value = words[2][:-1]
                                buy_price = words[4]
                                lotto = "LOTTO" in str(tweet)
                                self.__stock_alerts.append(StockAlert(ticker, buy_type, buy_value, buy_price, lotto))
                    self.__current_tweets = tweets.data
            except Exception:
                print("Twitter ping failed " + str(monotonic()))

    def get_back_test_time(self):
        return self.__back_test_time

    def get_tweets(self):
        return self.__current_tweets

    def get_stock_alerts(self):
        return self.__stock_alerts

class StockAlert():
    def __init__(self, ticker, buy_type, buy_value, buy_price, lotto):
        self.ticker = ticker
        self.buy_price = float(buy_price)
        if "c" in buy_type:
            self.buy_type = "call"
        else:
            self.buy_type = "put"
        self.buy_value = buy_value
        self.filled = False
        self.closed = False
        self.lotto = lotto
        self.option_amount = 0
        self.stop_loss_upper = 0.1
        self.stop_loss_lower = 0.1
        self.purchased = False
        self.__real_price = 0
        self.__stock_symbol = ""
        self.__order_id = None

    def get_option_type(self):
        if "call" in self.buy_type:
            return "CALL"
        else:
            return "PUT"

    def set_order_id(self, order_id):
        self.__order_id = order_id
    
    def get_order_id(self):
        return self.__order_id

    def set_purchase_price(self, real_price):
        self.__real_price = real_price

    def set_stock_symbol(self, symbol):
        self.__stock_symbol

    def get_stock_symbol(self, symbol):
        return self.__stock_symbol

    def get_purchase_price(self):
        return self.__real_price

    def get_option_ticker(self):
        return self.ticker[1:]

    def get_strike_price(self):
        return self.buy_value

    def get_last_price(self):
        return self.buy_price

    def __str__(self):
        return_string = "Ticker: " + self.ticker + "\n"
        return_string += "Option type: " + self.buy_type + "\n"
        return_string += "Option value: " + self.buy_value + "\n"
        return_string += "Bought price: " + self.buy_price + "\n"
        return_string += "Lotto: " + str(self.lotto) + "\n"
        return return_string

    def set_loss(self, stop_loss):
        self.stop_loss_lower = stop_loss[0]
        self.stop_loss_upper = stop_loss[1]
    
    def buy(self):
        print("Buying " + self.ticker + "...")

# stockChecker = TwitterStockChecker(start_time=datetime.now().replace(day=22, hour=0, minute=30), end_time=None, twitter_user_id=3690023483,api_keys_path='twitterkeys.ini')
# while(True):   
#     sleep(1)     
#     for alert in stockChecker.get_stock_alerts():
#         print(alert)