from Twitter import *

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


class SGTwitterTDParser():
    def __init__(self):
        self.__stock_alerts = []
        self.__old_tweets = []

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
            buy_price = float(split_text[4])
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
            self.__stock_alerts.append(stock_alert)
        elif alert_type == "scale" or alert_type == "exit":
            symbol = ""
            for text in split_text:
                if "$" in text:
                    symbol = text[1:]
            for alert in self.__stock_alerts:
                alert : StockAlertInfo
                if symbol == alert.stock:
                    stock_alert = alert.change_alert(alert_type)
        return stock_alert



