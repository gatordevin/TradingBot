from email import message
from SGBotV1 import SGBot
from TD import TD, TDOptionParams, TDOCOOrder
from Twitter import Twitter
from datetime import datetime, timedelta
from Parsers import SGTwitterTDParser
from time import sleep

td = TD(paper_trade_balance=10000)
account = td.get_accounts()[0]
print(account.current_trading_balance)

# twitter = Twitter()
# twitter_user = twitter.get_user("Ryan11D")

# parser = SGTwitterTDParser()

# bot = SGBot(
#     trading_strategy={
#         "trade_number_target" : 2,
#         "trade_lottos" : True,
#         "minimum_option_price" : 0.1,
#         "max_number_of_contracts" : 2,
#         "stop_limit_percent" : 0.2,
#         "stop_loss_percent" : -0.2,
#         "maximum_option_price" : 8.0,
#         "balance_limit" : 500,
#         "check_account_balance" : True,
#         "order_price" : "alert"
#     }, td_api=td, td_account=account
# )

# while True:
#     messages = twitter.get_user_messages(twitter_user)
#     # print(messages[0].text)
#     # for message in messages:
#     #     print(message)
#     stock_alerts = parser.parse_messages(messages)
#     for alert in stock_alerts:
#         print(alert.alert_type, alert.stock)
#     for stock_alert in stock_alerts:
#         td_order = bot.place_order(stock_alert)
#     sleep(1)
