from TwitterAPI import TwitterAPI
from TwitterStockParsers import SirGoldmanParser
from datetime import datetime, timedelta
from TDApi import TDApi, StockOrder
from time import sleep

twitter_api = TwitterAPI("config/twitterkeys.ini")
twitter_user = twitter_api.get_twitter_user("Ryan11D")

stock_parser = SirGoldmanParser()

td_api = TDApi("config/td_credentials.json")

tweets = twitter_user.get_daily_tweets(day=datetime.now()-timedelta(days=2),only_new=True)
stock_alerts = stock_parser.parse_tweets(tweets)
orders = td_api.create_orders(stock_alerts)
for position in td_api.stock_positions:
    position.update_position()
    sleep(1)