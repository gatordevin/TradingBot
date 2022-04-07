from TwitterChecker import *
from TDTradeBot import *
stockChecker = TwitterStockChecker(start_time=datetime.now()-timedelta(minutes=0), end_time=None, twitter_user_id=3690023483,api_keys_path='twitterkeys.ini', back_test_speed=3600)
tdTrader = TDTrader("config/td_credentials.json")

# print(tdTrader.trading_money())
# print(tdTrader.get_account_id())
# ticker, price = tdTrader.get_option("CAT", "PUT", 222.5)
# tdTrader.buy_oco_option(ticker, price, 1)

index = 0
while True:
    while(len(stockChecker.get_stock_alerts())==index):
        sleep(1)
        tdTrader.validate_key()
    ordered = tdTrader.fill_stock_alert(stockChecker.get_stock_alerts()[index], price_limit=650, scale_to_price=True)
    if ordered:
        while(True):
            tdTrader.validate_key()
            ordered = tdTrader.fill_stock_alert(stockChecker.get_stock_alerts()[index], price_limit=650, scale_to_price=True)
            sleep(1)
    index += 1