from Logger import logs
from TwitterAPI import TweetMessage
import re
from StockBotApi import StockAlert

class SirGoldmanParser():
    def __init__(self):
        logs.debug("Created Twitter Stock SirGoldmanParser")
        self.__entry_alerts = []

    def parse_tweets(self, tweets : list[TweetMessage]):
        logs.debug("Parsing tweets")
        stock_alerts = []
        for tweet in tweets:
            logs.debug("Parsing: " + str(tweet.text))
            command = self.get_command(tweet)
            if(command):
                logs.debug("Found alert command: " + command)
                stock = self.get_stock(tweet, command)
                if(stock):
                    logs.debug("Found stock symbol: " + stock)
                    price = self.get_price(tweet, command)
                    if(price):
                        logs.debug("Found price: " + str(price))
                    strike_info = self.get_strike_price(tweet, command)
                    strike_price, contract_type = [None, None]
                    if(strike_info):
                        strike_price, contract_type = strike_info
                        logs.debug("Found strike price: " + str(strike_price) + " " + contract_type)
                    stock_alert = None
                    if(command=="entry"):
                        logs.debug("Found new position entry: " + stock)
                        stock_alert = StockAlert(command, stock, price, strike_price, contract_type, tweet.date, tweet)
                        self.__entry_alerts.append(stock_alert)
                    elif(command=="exit"):
                        paired_entry_alert = None
                        for entry_alert in self.__entry_alerts:
                            entry_alert : StockAlert
                            if(entry_alert.stock==stock):
                                logs.debug("Found position exit: " + stock)
                                paired_entry_alert = entry_alert
                                stock_alert = StockAlert(command, stock, price, entry_alert.strike_price, entry_alert.contract_type, tweet.date, tweet)
                                break
                        if(stock_alert==None):
                            logs.debug("Found exit command with no entry: " + stock)
                            stock_alert = StockAlert(command, stock, price, strike_price, contract_type, tweet.date, tweet)
                        if(paired_entry_alert!=None):
                            self.__entry_alerts.remove(paired_entry_alert)
                        stock_alerts.append(stock_alert)
                    else:
                        for entry_alert in self.__entry_alerts:
                            entry_alert : StockAlert
                            if(entry_alert.stock==stock):
                                logs.debug("Found position command with entry: " + stock)
                                stock_alert = StockAlert(command, stock, price, entry_alert.strike_price, entry_alert.contract_type, tweet.date, tweet)
                                break
                        if(stock_alert==None):
                            logs.debug("Found position command with no entry: " + stock)
                            stock_alert = StockAlert(command, stock, price, strike_price, contract_type, tweet.date, tweet)
                        stock_alerts.append(stock_alert)
        return stock_alerts

    def get_strike_price(self, tweet, command):
        logs.debug("Parsing tweet for strike price")
        if(command=="entry"):
            split_text = str(tweet.text).split(" ")
            strike_info = split_text[2]
            strike_price = strike_info[:-1]
            if(strike_info[-1:]=="c"):
                contract_type = "call"
            else:
                contract_type = "put"
            return strike_price, contract_type

    def get_command(self, tweet):
        logs.debug("Parsing tweet for command string")
        split_text = str(tweet.text).split(" ")
        command = split_text[0]
        if "entry" or "scale" or "exit" in command:
            return command
        else:
            return None

    def get_stock(self, tweet, command):
        logs.debug("Parsing tweet for stock symbol")
        split_text = str(tweet.text).split(" ")
        stock_symbol = None
        for text in split_text:
            if "$" in text:
                stock_symbol = re.sub(r'[^a-zA-Z ]+', '', text)
                return stock_symbol
        return stock_symbol

    def get_price(self, tweet, command):
        logs.debug("Parsing tweet for price value")
        split_text = str(tweet.text).split(" ")
        if(command=="entry"):
            for idx, text in enumerate(split_text):
                if "@" in text:
                    return float(split_text[idx+1])
        else:
            return None