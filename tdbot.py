import requests
from pprint import pprint
import configparser
from td.credentials import TdCredentials
from td.client import TdAmeritradeClient
from td.utils import *
from td import *

config = configparser.ConfigParser(interpolation=None)
config.read('tdkeys.ini')

client_id = config['td']['ClientId']
redirect_uri = config['td']['RedirectUri']
authorization_code = config['td']['AuthorizationCode']
access_token = config['td']['AccessToken']
refresh_token = config['td']['RefreshToken']

# Intialize our `Credentials` object.
td_credentials = TdCredentials(
    client_id=client_id,
    redirect_uri=redirect_uri,
    credential_file='config/td_credentials.json'
)

# Initalize the `TdAmeritradeClient`
td_client = TdAmeritradeClient(
    credentials=td_credentials
)

options_service = td_client.options_chain()
option_chain_dict = {
        'symbol': 'MSFT',
        'contractType': 'CALL',
        'expirationMonth': 'JUN',
        'optionType': 'SC',
        'range': 'ITM',
        'includeQuotes': True
    }
print(options_service.get_option_chain(option_chain_dict=option_chain_dict))

order_service = td_client.orders()

# order_service.
# Initialize the Quotes service.
quote_service = td_client.quotes()

# Grab a single quote.
# pprint(
#     quote_service.get_quote(instrument='AAPL')
# )

# # Grab multiple quotes.
# pprint(
#     quote_service.get_quotes(instruments=['AAPL', 'SQ'])
# )