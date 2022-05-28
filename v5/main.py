# StockInfoSource -> StockInfoSink-StockAlertSource -> StockAlertSink-StockPurchaseSource -> StockPurchaseSink
# BrokerInfoSource -> BrokerInfoSink

from time import sleep
from StockBroker import TDInfoSource, StockBrokerSink
from StockInfo import TwitterUserStockInfo
from datetime import datetime, timedelta
from StockAlert import SirGoldmanTwitterMessageSink

class StockInfo(StockBrokerSink):
    def __init__(self):
        super().__init__()

    def on_broker_sink(self, data: dict):
        print(data)

stock_info = TwitterUserStockInfo("RyansTrading_", live=False, start_time=datetime.now()-timedelta(days=3))
stock_alert = SirGoldmanTwitterMessageSink()
stock_broker = TDInfoSource()
stock_data = StockInfo()
# Add support for buying stock alerts
stock_info.add_sink(stock_alert)
stock_broker.add_broker_sink(stock_data)
google_stock = stock_broker.symbol_listen("GOOG")
while(True):
    print(google_stock.ask_price)
    sleep(1000)