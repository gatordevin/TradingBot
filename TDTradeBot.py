from time import strftime
import requests
from pprint import pprint
import configparser
from td.credentials import TdCredentials
from td.client import TdAmeritradeClient
from td.utils import *
from td import *
from datetime import date, datetime, timedelta
from time import sleep, monotonic
from td.utils.orders import Order
from math import floor
from TwitterChecker import StockAlert
import os
import json

class TDTrader():
    def __init__(self, config_file):
        self.config_file = config_file
        self.init_td()
    
    def init_td(self):
        # config = configparser.ConfigParser(interpolation=None)
        # config.read(self.config_file)

        # self.__client_id = config['td']['ClientId']
        # self.__redirect_uri = config['td']['RedirectUri']
        # self.__authorization_code = config['td']['AuthorizationCode']
        # self.__access_token = config['td']['AccessToken']
        # self.__refresh_token = config['td']['RefreshToken']
        if not os.path.isfile(self.config_file):
            self.__client_id = input("Client ID: ")
            self.__redirect_url = input("Redirect Url: ")
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            self.__td_credentials = TdCredentials(
                client_id=self.__client_id,
                redirect_uri=self.__redirect_url,
                make_file=self.config_file
            )
        else:
            self.__json_dict = json.load(open(self.config_file))
            self.__td_credentials = TdCredentials(
                client_id=self.__json_dict["client_id"],
                redirect_uri=self.__json_dict["redirect_url"],
                credential_file=self.config_file
            )
        print("Got key an initialized API")
        # Initalize the `TdAmeritradeClient`
        self.__td_client = TdAmeritradeClient(
            credentials=self.__td_credentials
        )
        self.__options_service = self.__td_client.options_chain()
        self.__account_service = self.__td_client.accounts()
        self.__order_service = self.__td_client.orders()

    def validate_key(self):
        for i in range(5):
            try:
                self.__td_credentials.validate_token()
                sleep(0.5)
                break
            except requests.HTTPError as e:
                print("Failed to validate token")

    def trading_money(self):
        return self.__account_service.get_accounts()[0]["securitiesAccount"]["currentBalances"]["cashAvailableForTrading"]

    def fill_stock_alert(self, stockAlert : StockAlert, quantity=1, price_limit=300, scale_to_price=False):
        if( not stockAlert.purchased and not stockAlert.lotto):
            option_data = self.get_option(stockAlert.get_option_ticker(), stockAlert.get_option_type(), stockAlert.get_strike_price())
            if(option_data!=None):
                option_symbol, current_price = option_data
                print(stockAlert.get_option_ticker() + ": Our buy price: " + str(current_price) + " His Buy Price: " + str(stockAlert.get_last_price()))
                # if(float(stockAlert.get_last_price())*0.98<current_price<float(stockAlert.get_last_price())*1.02):
                stockAlert.purchased = True
                stockAlert.set_purchase_price(current_price)
                order_id = self.buy_oco_option(option_symbol, stockAlert.get_last_price(), quantity, price_limit=price_limit, scale_to_price=scale_to_price)
                if(order_id==None):
                    print("order cancelled")
                stockAlert.set_order_id(order_id)
                return True
            return False
        else:
            option_data = self.get_option(stockAlert.get_option_ticker(), stockAlert.get_option_type(), stockAlert.get_strike_price())
            if(option_data!=None):
                option_symbol, current_price = option_data
                percent = (((current_price*100)-1 / (stockAlert.get_last_price())*100)-1)*100
                print(stockAlert.get_option_ticker() + ": stock order placed: Return: " + str(percent))
            return False

    def get_option(self, ticker, option_type, price):
        start = datetime.now() - timedelta(days=datetime.now().weekday())
        end = start + timedelta(days=4)
        option_chain_dict = {
            'symbol': ticker,
            'contractType': option_type,
            'toDate': end.strftime("%Y-%m-%d"),
            'optionType': 'ALL',
            'range': 'NTM',
            'includeQuotes': True,
            'strike': price
        }
        if(option_type=="CALL"):
            ExpDateMap = "callExpDateMap"
        else:
            ExpDateMap = "putExpDateMap"
        option_chain = None
        for i in range(10):
            try:
                sleep(0.5)
                option_chain = self.__options_service.get_option_chain(option_chain_dict=option_chain_dict)
                break
            except requests.HTTPError as e:
                print("Could not get option chain")
        if(option_chain):
            if(option_chain["status"]=="SUCCESS"):
                expDate = list(option_chain[ExpDateMap].keys())[0]
                option = option_chain[ExpDateMap][expDate][str(float(price))][0]
                return [option["symbol"],option["last"]]
        return None

    def get_account_id(self):
        return self.__account_service.get_accounts()[0]["securitiesAccount"]["accountId"]

    def buy_oco_option(self, option_ticker, price, amount, price_limit=600, scale_to_price=False):
        if(scale_to_price):
            amount=floor(price_limit/(price*100))
        net = price*amount*100
        print(net)
        print(self.trading_money())
        print(price_limit)
        if float(net)<=float(self.trading_money()) and float(net)<=float(price_limit):
            print("Making " + str(net) + "$ order of " + option_ticker)
            order = self.__order_service.place_order(account_id=self.get_account_id(),order_dict={
                "orderStrategyType": "TRIGGER",
                "session": "NORMAL",
                "duration": "DAY",
                "orderType": "LIMIT",
                "price": price,
                "orderLegCollection": [
                    {
                    "instruction": "BUY_TO_OPEN",
                    "quantity": amount,
                    "instrument": {
                        "assetType": "OPTION",
                        "symbol": option_ticker
                    }
                    }
                ],
                "childOrderStrategies": [
                    {
                    "orderStrategyType": "OCO",
                    "childOrderStrategies": [
                        {
                        "orderStrategyType": "SINGLE",
                        "session": "NORMAL",
                        "duration": "GOOD_TILL_CANCEL",
                        "orderType": "LIMIT",
                        "price": round(price*1.1,2),
                        "orderLegCollection": [
                            {
                            "instruction": "SELL_TO_OPEN",
                            "quantity": amount,
                            "instrument": {
                                "assetType": "OPTION",
                                "symbol": option_ticker
                            }
                            }
                        ]
                        },
                        {
                        "orderStrategyType": "SINGLE",
                        "session": "NORMAL",
                        "duration": "GOOD_TILL_CANCEL",
                        "orderType": "STOP",
                        "stopPrice": round(price*0.9,2),
                        "orderLegCollection": [
                            {
                            "instruction": "SELL_TO_OPEN",
                            "quantity": amount,
                            "instrument": {
                                "assetType": "OPTION",
                                "symbol": option_ticker 
                            }
                            }
                        ]
                        }
                    ]
                    }
                ]
                })
            order_id = self.get_most_recent_order_id()
            start_time = monotonic()

            # print(self.order_filled(order_id))
            while monotonic()-start_time<5 and not self.order_filled(order_id):
                sleep(1)
            # print(self.order_filled(order_id))
            if not self.order_filled(order_id):
                self.__order_service.cancel_order(self.get_account_id(), order_id)
                return None
            print("order filled")
            return order_id
            return None
        else:
            print("Out of budget")
            return None

    def get_orders(self, order_id=None):
        if(order_id==None):
            order = self.__order_service.get_orders_by_query(self.get_account_id(), from_entered_time=datetime.today())
        else:
            order = self.__order_service.get_order(self.get_account_id(), order_id)
        return order
    
    def get_most_recent_order_id(self):
        return self.get_orders()[0]["orderId"]

    def order_filled(self, order_id):
        return "PENDING_ACTIVATION" not in self.get_orders(order_id)["status"]

# option_chain_dict = {
#         'symbol': 'MSFT',
#         'contractType': 'CALL',
#         'expirationMonth': 'JUN',
#         'optionType': 'SC',
#         'range': 'ITM',
#         'includeQuotes': True
#     }
# print(options_service.get_option_chain(option_chain_dict=option_chain_dict))

# order_service = td_client.orders()

# # order_service.
# # Initialize the Quotes service.
# quote_service = td_client.quotes()

# # Grab a single quote.
# # pprint(
# #     quote_service.get_quote(instrument='AAPL')
# # )

# # # Grab multiple quotes.
# # pprint(
# #     quote_service.get_quotes(instruments=['AAPL', 'SQ'])
# # )