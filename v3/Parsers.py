from Twitter import *
import re

class StockAlertInfo():
    def __init__(self, alert_info : dict):
        self.__alert_info : dict = alert_info
        self.stock = self.__alert_info["stock"]
        self.buy_price = self.__alert_info["buy_price"]
        self.option = self.__alert_info["option"]
        self.alert_type = self.__alert_info["alert_type"]
        self.lotto = self.__alert_info["lotto"]
        self.alert_time = self.__alert_info["time"]
        self.time = datetime.now()
        if(self.option):
            self.strike_price = self.__alert_info["strike_price"]
            self.contract_type = self.__alert_info["contract_type"]

    def change_alert(self, alert_type):
        alert_info = self.__alert_info
        alert_info["alert_type"] = alert_type
        stock_alert = StockAlertInfo(alert_info)
        return stock_alert

class DailyRecap():
    def __init__(self, daily_alerts : list[StockAlertInfo, float]):
        self.__daily_alerts : list[StockAlertInfo, float] = daily_alerts
    
    def get_stocks(self):
        for stock_alert, sell_price in self.__daily_alerts:
            yield stock_alert, sell_price

class SGTwitterTDParser():
    def __init__(self):
        self.__stock_alerts = []
        self.__old_tweets = []
        self.daily_recaps = []
        self.__daily_alerts = []
    
    def parse_messages(self, twitter_messages : list[TwitterMessage]) -> list[StockAlertInfo]:
        stock_alerts = []
        for message in twitter_messages:
            stock_alert = self.parse_message(message)
            if stock_alert:
                stock_alerts.append(stock_alert)
        return stock_alerts

    def parse_message(self, twitter_message : TwitterMessage) -> StockAlertInfo:
        for old_tweets in self.__old_tweets:
            if twitter_message.id == old_tweets.id:
                return None
        self.__old_tweets.append(twitter_message)
        tweet_text = twitter_message.text
        split_text = tweet_text.split(" ")
        if "DAILY RECAP" in tweet_text:
            daily_alerts = []
            split_text_copy = split_text
            daily_alerts_filtered = []
            for daily_alert in self.__daily_alerts:
                daily_alert : StockAlertInfo
                adjusted_split_text : list = split_text_copy
                for idx, split in enumerate(split_text):
                    if daily_alert.stock in split:
                        price = re.sub("[^0123456789\.]","",split_text[idx+1])
                        if price == "":
                            pass
                        else:
                            price = float(price)
                        if "@" not in split_text[idx+2] and daily_alert.buy_price == price:
                            if "(" in split_text[idx+3]:
                                potential_sell = split_text[idx+3].split("(")[0]
                                if potential_sell != "":
                                    sell_price = potential_sell
                                else:
                                    sell_price = split_text[idx+2]
                            else:
                                sell_price = split_text[idx+3]
                            daily_alerts_filtered.append([daily_alert, float(re.sub("[^0123456789\.]","",sell_price))])
                            adjusted_split_text.pop(idx)
                            break
                        else:
                            daily_alerts.append(daily_alert)
                split_text_copy = adjusted_split_text
            daily_recap = DailyRecap(daily_alerts_filtered)
            self.daily_recaps.append(daily_recap)
            self.__daily_alerts = daily_alerts
        alert_type = split_text[0]
        stock_alert = None
        option = True
        if alert_type == "entry":
            symbol = split_text[1][1:]
            strike_price = split_text[2][:-1]
            contract_type = ""
            if split_text[2][-1] == "c":
                contract_type = "CALL"
            else:
                contract_type = "PUT"
            buy_price = None
            for idx, split in enumerate(split_text):
                if split == "@":
                    buy_price = float(split_text[idx+1])
                    break
            if buy_price == None:
                buy_price = float(split_text[3])
            lotto = False
            for split in split_text:
                if split == "lotto" or split == "LOTTO":
                    lotto = True
            alert_info = {
                "stock" : symbol,
                "buy_price" : buy_price,
                "option" : option,
                "alert_type" : alert_type,
                "lotto" : lotto,
                "strike_price" : strike_price,
                "contract_type" : contract_type,
                "time" : twitter_message.created
            }
            stock_alert = StockAlertInfo(alert_info)
            self.__daily_alerts.append(stock_alert)
            self.__stock_alerts.append(stock_alert)
        elif alert_type == "scale" or alert_type == "exit":
            symbol = ""
            for text in split_text:
                if "$" in text:
                    symbol = text[1:]
            reversed_alerts = self.__stock_alerts
            reversed_alerts.reverse()
            for alert in reversed_alerts:
                alert : StockAlertInfo
                if symbol == alert.stock:
                    stock_alert = alert.change_alert(alert_type)
        return stock_alert



