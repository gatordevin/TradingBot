import json
import requests
from TDApi import TDApi, StockOrder, StockAlert
from datetime import date, datetime
from BackTesting import BackTest

from TDApi import StockPosition
from datetime import datetime, timedelta

response = requests.get("https://apewisdom.io/api/v1.0/filter/all-stocks/page/1")
json_data = json.loads(response.text)

current_time = datetime.now()
back_test = BackTest(current_time-timedelta(days=30), current_time, 60)

td_api = TDApi("config/td_credentials.json", paper_trading=True, back_test=back_test)

for time in back_test.start():
    time : datetime
    stock_alert = StockAlert("entry", "SPY", 0, None, None, time, "", quantity=1)
    order = td_api.create_order(stock_alert)
    order.fill_order()
    break

    
# stock_alerts = [StockAlert("entry", result["ticker"], 0, None, None, datetime.now(), result, quantity=1) for result in json_data["results"][0:15]]

# orders = td_api.create_orders(stock_alerts)

# orders : list[StockOrder]
# print(td_api.starting_balance)
# orders[0].fill_order()
# print(td_api.starting_balance)
# for position in td_api.stock_positions:
#     position : StockPosition
#     print(position.stock_orders)
