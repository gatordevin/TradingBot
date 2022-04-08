from datetime import datetime, timedelta
from Parsers import DailyRecap, SGTwitterTDParser, StockAlertInfo
from Twitter import Twitter
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
import seaborn as sns

twitter = Twitter()
twitter_user = twitter.get_user("Ryan11D")
parser = SGTwitterTDParser()

messages = twitter.get_user_messages(twitter_user,start_time=None, max_results=200)
# print(len(messages))
parser.parse_messages(messages)

percent_changes = []
max_percent_tweet = [None, 0]
for daily_recap in parser.daily_recaps:
    daily_recap : DailyRecap
    for stock_alert, sell_price in daily_recap.get_stocks():
        stock_alert : StockAlertInfo
        percent_change = (sell_price-stock_alert.buy_price)/stock_alert.buy_price
        if(max_percent_tweet[1]<percent_change):
            max_percent_tweet = [stock_alert, sell_price]
        percent_changes.append(percent_change)
# print(sum(percent_changes)/len(percent_changes))
# print(percent_changes)

total_increase = 1.0
for percent_change in percent_changes:
    total_increase *= (percent_change+1)
    print(percent_change)

print(total_increase)

percent_changes = [ x for x in percent_changes if -1 <= x <= 1 ]

# print(max_percent_tweet[0].stock, max_percent_tweet[0].alert_time, max_percent_tweet[0].buy_price, max_percent_tweet[1])
sns.set_style('whitegrid')
sns.kdeplot(np.array(percent_changes), bw=0.1)
plt.show()