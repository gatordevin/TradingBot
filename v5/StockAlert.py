import re
from StockInfo import StockInfoSink
from Twitter import TwitterMessage
from datetime import datetime

class DailyRecapAlertSink():
    def __init__(self):
        super().__init__()
        pass

    def on_recap_sink(self, data : dict):
        pass

class DailyRecapAlertSource():
    def __init__(self):
        self.__daily_recap_sinks : list[DailyRecapAlertSink] = []
        super().__init__()

    def ad_recap_sink(self, sink : DailyRecapAlertSink):
        self.__daily_recap_sinks.append(sink)

    def on_recap_source(self, data : dict):
        for sink in self.__daily_recap_sinks:
            sink.on_recap_sink(data)


class StockAlertSink():
    def __init__(self):
        super().__init__()
        pass

    def on_data_sink(self, data : dict):
        pass

class StockAlertInfo():
    def __init__(self, alert_info : dict):
        self.__alert_info : dict = alert_info
        self.stock = self.__alert_info["stock"]
        self.option = self.__alert_info["option"]
        self.alert_type = self.__alert_info["alert_type"]
        self.extra_info = self.__alert_info.get("extra_info", {})
        self.time = datetime.now()
        if(self.option):
            self.strike_price = self.__alert_info["strike_price"]
            self.contract_type = self.__alert_info["contract_type"]

    def get_alert_info(self):
        return self.__alert_info

class DailyRecap():
    def __init__(self):
        super().__init__()
        self.__daily_alerts : list[StockAlertInfo, StockAlertInfo] = []
    
    def get_stocks(self):
        for stock_alert, sell_alert in self.__daily_alerts:
            yield stock_alert, sell_alert

    def add_stock(self, entry_alert, exit_alert):
        self.__daily_alerts.append([entry_alert,exit_alert])

class StockAlertSource():
    def __init__(self):
        super().__init__()
        self.__stock_alert_sinks : list[StockAlertSink] = []

    def add_stock_alert_sink(self, sink : StockAlertSink):
        self.__stock_alert_sinks.append(sink)

    def on_stock_alert_source(self, data : dict):
        for sink in self.__stock_alert_sinks:
            sink.on_data_sink(data)

class SirGoldmanTwitterMessageSink(StockInfoSink, StockAlertSource, DailyRecapAlertSource):
    def __init__(self):
        self.__active_alerts = []
        self.__unrecapped_alerts = []
        self.__entry_alerts = []
        self.__scale_alerts = []
        self.__exit_alerts = []
        super(SirGoldmanTwitterMessageSink, self).__init__()

    def is_daily(self, message : TwitterMessage):
        if "DAILY RECAP" in message.text:
            return True
        return False

    def parse_daily(self, message : TwitterMessage):
        message_split = message.text.split(" ")
        unrecapped_alerts : list[StockAlertInfo] = self.__unrecapped_alerts
        daily_recap = DailyRecap()
        for alert in unrecapped_alerts:
            adjusted_message_split = message_split
            for idx, split in enumerate(adjusted_message_split):
                price = re.sub("[^0123456789\.]","",message_split[idx+1])
                if price != "":
                    price = float(price)
                if "@" not in message_split[idx+2] and alert.extra_info.get("alert_price", 0) == price:
                    if "(" in message_split[idx+3]:
                        potential_sell = message_split[idx+3].split("(")[0]
                        if potential_sell != "":
                            sell_price = potential_sell
                        else:
                            sell_price = message_split[idx+2]
                    else:
                        sell_price = message_split[idx+3]
                    sell_price = float(re.sub("[^0123456789\.]","",sell_price))
                    sell_alert = None
                    reversed_exit_alerts = self.__exit_alerts
                    for exit_alert in reversed_exit_alerts:
                        exit_alert : StockAlertInfo
                        if exit_alert.extra_info.get("alert_price", 0) == sell_price and exit_alert.stock == alert.stock:
                            sell_alert = exit_alert
                            break
                    self.__unrecapped_alerts.remove(alert)
                    daily_recap.add_stock(alert, sell_alert)
                    message_split.pop(idx)
                    break
        return daily_recap
                    


    def is_alert(self, message : TwitterMessage):
        alert_type = message.text.split(" ")[0]
        if alert_type in ["entry", "scale", "exit"]:
            return alert_type
        return None

    def parse_alert(self, message : TwitterMessage):
        split_message = message.text.split(" ")
        alert_type = split_message[0]
        stock_alert = None
        if alert_type == "entry":
            stock_alert = self.parse_entry(message)
        elif alert_type == "scale":
            stock_alert = self.parse_scale(message)
        elif alert_type == "exit":
            stock_alert = self.parse_exit(message)
        return stock_alert

    def parse_entry(self, message : TwitterMessage):
        split_message = message.text.split(" ")
        alert_type = split_message[0]
        symbol = split_message[1][1:]
        strike_price = split_message[2][:-1]
        option = True

        contract_type = ""
        if split_message[2][-1] == "c":
            contract_type = "CALL"
        elif split_message[2][-1] == "p":
            contract_type = "PUT"
        
        buy_price = None
        for idx, split in enumerate(split_message):
            if split == "@":
                buy_price = float(split_message[idx+1])
                break
        if buy_price == None:
            buy_price = float(split_message[3])

        lotto = False
        for split in split_message:
            if split in ["lotto","LOTTO","RISKY","risky]"]:
                lotto = True

        alert_info = {
                "stock" : symbol,
                "option" : option,
                "alert_type" : alert_type,
                "strike_price" : strike_price,
                "contract_type" : contract_type,
                "extra_info" : {
                    "time" : message.created,
                    "alert_price" : buy_price,
                    "lotto" : lotto
                }
            }
        stock_alert = StockAlertInfo(alert_info)
        self.__active_alerts.append(stock_alert)
        self.__entry_alerts.append(stock_alert)
        self.__unrecapped_alerts.append(stock_alert)
        return stock_alert

    def parse_scale(self, message : TwitterMessage):
        split_message = message.text.split(" ")
        alert_type = split_message[0]
        symbol = ""
        for text in split_message:
            if "$" in text:
                symbol = text[1:]
        reversed_alerts = self.__entry_alerts
        reversed_alerts.reverse()
        for alert in reversed_alerts:
            alert : StockAlertInfo
            if symbol == alert.stock:
                alert_dict = alert.get_alert_info()
                alert_dict["alert_type"] = alert_type
                stock_alert = StockAlertInfo(alert_dict)
                self.__scale_alerts.append(stock_alert)
                return stock_alert

    def parse_exit(self, message : TwitterMessage):
        split_message = message.text.split(" ")
        alert_type = split_message[0]
        symbol = ""
        for text in split_message:
            if "$" in text:
                symbol = text[1:]
        reversed_alerts = self.__entry_alerts
        reversed_alerts.reverse()
        for alert in reversed_alerts:
            alert : StockAlertInfo
            if symbol == alert.stock:
                alert_dict = alert.get_alert_info()
                alert_dict["alert_type"] = alert_type
                stock_alert = StockAlertInfo(alert_dict)
                self.__exit_alerts.append(stock_alert)
                self.__active_alerts.remove(alert)
                return stock_alert

    def on_data_sink(self, data : TwitterMessage):
        if self.is_daily(data):
            daily_recap = self.parse_daily(data)
            if daily_recap:
                print(daily_recap)
                self.on_recap_source(daily_recap)
        elif self.is_alert(data):
            stock_alert = self.parse_alert(data)
            if stock_alert:
                print(stock_alert)
                self.on_stock_alert_source(stock_alert)