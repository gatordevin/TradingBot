# StockInfoSource -> StockInfoSink-StockAlertSource -> StockAlertSink-StockPurchaseSource -> StockPurchaseSink
# BrokerInfoSource -> BrokerInfoSink

from time import sleep
from StockBroker import TDInfoSource, StockBrokerSink
from TD import TDSymbol, TDStockOrder
from StockInfo import TwitterUserStockInfo
from datetime import datetime, timedelta
from StockAlert import SirGoldmanTwitterMessageSink

class StockInfo(StockBrokerSink):
    def __init__(self):
        super().__init__()

    def on_broker_sink(self, data: TDSymbol):
        print(data)

stock_info = TwitterUserStockInfo("RyansTrading_", live=False, start_time=datetime.now()-timedelta(days=3))
stock_alert = SirGoldmanTwitterMessageSink()
stock_broker = TDInfoSource()
stock_data = StockInfo()

stock_info.add_sink(stock_alert)
stock_broker.add_broker_sink(stock_data)
google_stock = stock_broker.symbol_listen("GOOG")

td_account = stock_broker.get_td_account()
td_api = stock_broker.get_td_api()

#Example place simple limit order of stock order
order = TDStockOrder(google_stock, 1, google_stock.ask_price)
td_api.fill_order(order, td_account)

while(True):
    print(google_stock.ask_price)
    sleep(1000)