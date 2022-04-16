# StockInfoSource -> StockInfoSink-StockAlertSource -> StockAlertSink-StockPurchaseSource -> StockPurchaseSink
# BrokerInfoSource -> BrokerInfoSink

from time import sleep
from StockInfo import TwitterUserStockInfo
from datetime import datetime, timedelta
from StockAlert import SirGoldmanTwitterMessageSink

stock_info = TwitterUserStockInfo("Ryan11D", live=False, start_time=datetime.now()-timedelta(days=3))
stock_alert = SirGoldmanTwitterMessageSink()

stock_info.add_sink(stock_alert)
# stock_info.begin()
print("added sink")
while(True):
    sleep(1)