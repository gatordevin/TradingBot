from time import sleep
from Parsers import SGTwitterTDParser
from SGBotV1 import SGBot
from TD import TD, TDOCOOrder, TDOption, TDOrder
from time import sleep, monotonic
from Twitter import Twitter

td_api = TD() #paper_trading_file="trading/test.json"
twitter_api = Twitter()
user = twitter_api.get_user("Ryan11D")
parser = SGTwitterTDParser()

account = td_api.accounts[0]
# google_stock = account.get_stock('GOOG')
google_option : TDOption = account.get_option('GOOG', "CALL",2625,7)

# print("amd added")
# amd = account.get_stock('AMD')

# print("Stock price: " + str(amd.ask_price))

bot = SGBot(
    trading_strategy={
        "trade_number_target" : 2,
        "trade_lottos" : False,
        "minimum_option_price" : 0.1,
        "max_number_of_contracts" : 6,
        "stop_limit_percent" : 0.2,
        "stop_loss_percent" : -0.2,
        "maximum_option_price" : 8.0,
        "balance_limit" : 400,
        "check_account_balance" : True,
        "order_price" : "alert"
    }, td_api=td_api, td_account=account
)

while(True):
    
    # print(google_option.ask)
    bought_options=[]
    if(user.is_new_tweets()):
        new_tweets = user.get_new_tweets()
        for tweet in new_tweets:
            print(tweet.text)
        stock_alerts = parser.parse_messages(new_tweets)
        for stock_alert in stock_alerts:
            order = bot.place_order(stock_alert)
            if order is not None:
                option, order_price = order
                bought_options.append([option, order_price])
    else:
        for option, order_price in bought_options:
            option : TDOption
            percent_increase = (((option.multiplier*option.bid)-order_price)/order_price)*100
            print(option.symbol + " " + str(percent_increase))
    sleep(0.5)
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
#     }, td_api=td_api, td_account=account
# )

# while(True):
#     if(user.is_new_tweets()):
#         new_tweets = user.get_new_tweets()
#         stock_alerts = parser.parse_messages(new_tweets)
#         for alert in stock_alerts:
#             print(alert.alert_type, alert.stock)
#         for stock_alert in stock_alerts:
#             td_order = bot.place_order(stock_alert)
#     else:
#         pass