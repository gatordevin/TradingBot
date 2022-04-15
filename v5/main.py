# StockInfoSource -> StockInfoSink-StockAlertSource -> StockAlertSink-StockPurchaseSource -> StockPurchaseSink
# BrokerInfoSource -> BrokerInfoSink

from time import sleep
from StockInfo import TwitterUserStockInfo
from datetime import datetime, timedelta

stock_info = TwitterUserStockInfo("Ryan11D", live=False, start_time=datetime.now()-timedelta(days=3))

while(True):
    sleep(1)