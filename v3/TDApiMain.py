import json
from Authenticator import TDApiAuthenticator
from tda import client
from tda.streaming import StreamClient
import xmltodict
import asyncio
import json
# token_path = '/path/to/token.json'
# api_key = 'YOUR_API_KEY@AMER.OAUTHAP'
# redirect_uri = 'https://your.redirecturi.com'

# try:
#     c = auth.client_from_token_file(token_path, api_key)
# except FileNotFoundError:
#     from selenium import webdriver
#     with webdriver.Chrome() as driver:
#         c = auth.client_from_login_flow(
#             driver, api_key, redirect_uri, token_path)

auth = TDApiAuthenticator()
td_client = auth.get_client()
account_id = td_client.get_accounts().json()[0]["securitiesAccount"]["accountId"]
stream_client = StreamClient(td_client, account_id=account_id)

async def read_stream():
        await stream_client.login()
        await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

        def print_message(message):
                json_data = message
                print(json_data)
                if json_data["service"] == "ACCT_ACTIVITY":
                        content = json_data["content"][0]
                        # print(content["MESSAGE_DATA"])
                        if(content["MESSAGE_DATA"] != ""):
                                my_dict = xmltodict.parse(content["MESSAGE_DATA"])
                                print(my_dict)
                # print(json_data)


        # Always add handlers before subscribing because many streams start sending
        # data immediately after success, and messages with no handlers are dropped.
        #     stream_client.add_nasdaq_book_handler(print_message)
        stream_client.add_account_activity_handler(print_message)
        stream_client.add_level_one_option_handler(print_message)

        await stream_client.account_activity_sub()

        while True:
                await stream_client.handle_message()

asyncio.run(read_stream())
print("test")

# r = td_client.get_price_history('AAPL',
#         period_type=client.Client.PriceHistory.PeriodType.DAY,
#         period=client.Client.PriceHistory.Period.FIVE_DAYS,
#         frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
#         frequency=client.Client.PriceHistory.Frequency.EVERY_MINUTE)
# assert r.status_code == 200, r.raise_for_status()
# # print(json.dumps(r.json(), indent=4))