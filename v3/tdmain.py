from email import message
from SGBotV1 import SGBot
from TD import TD, TDOptionParams, TDOCOOrder
from Twitter import Twitter
from datetime import datetime, timedelta
from Parsers import SGTwitterTDParser
from time import sleep

td = TD()
account = td.get_accounts()[0]

twitter = Twitter()
twitter_user = twitter.get_user("Ryan11D")

parser = SGTwitterTDParser()

bot = SGBot(
    trading_strategy={
        "trade_number_target" : 1,
        "trade_lottos" : False,
        "minimum_option_price" : 0.8,
        "stop_limit_percent" : 0.1,
        "stop_loss_percent" : -0.1,
        "maximum_option_price" : 8.0,
        "balance_limit" : 590
    }, td_api=td, td_account=account
)

while True:
    messages = twitter.get_user_messages(twitter_user, datetime.now())
    stock_alerts = parser.parse_messages(messages)
    for alert in stock_alerts:
        print(alert.alert_type, alert.stock)
    for stock_alert in stock_alerts:
        td_order = bot.place_order(stock_alert)
    sleep(1)
