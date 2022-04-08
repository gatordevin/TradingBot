from datetime import datetime, timedelta
from Parsers import SGTwitterTDParser
from Twitter import Twitter

twitter = Twitter()
twitter_user = twitter.get_user("Ryan11D")
parser = SGTwitterTDParser()

messages = twitter.get_user_messages(twitter_user,start_time=None, max_results=200)

parser.parse_messages(messages)

print(parser.daily_recaps)

