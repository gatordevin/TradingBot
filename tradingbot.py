from TwitterChecker import *

stockChecker = TwitterStockChecker(start_time=datetime.now().replace(day=22, hour=0, minute=30), end_time=None, twitter_user_id=3690023483,api_keys_path='twitterkeys.ini')
while(True):   
    sleep(1)     
    for alert in stockChecker.get_stock_alerts():
        print(alert)