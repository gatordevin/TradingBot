from TwitterChecker import *
from TDTradeBot import *
stockChecker = TwitterStockChecker(start_time=datetime.now()-timedelta(minutes=0), end_time=None, twitter_user_id=3690023483,api_keys_path='twitterkeys.ini', back_test_speed=3600)
tdTrader = TDTrader("config/td_credentials.json")

# print(tdTrader.trading_money())
# print(tdTrader.get_account_id())
# ticker, price = tdTrader.get_option("CAT", "PUT", 222.5)
# tdTrader.buy_oco_option(ticker, price, 1)

while(stockChecker.get_stock_alerts()==[]):
    sleep(1)
    tdTrader.validate_key()
# order = tdTrader.get_most_recent_order_id()
while(True):
    # print(tdTrader.order_filled(order["orderId"]))
    tdTrader.validate_key()
    tdTrader.fill_stock_alert(stockChecker.get_stock_alerts()[0], price_limit=600, scale_to_price=True)
    sleep(1)