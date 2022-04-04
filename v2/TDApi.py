

from tracemalloc import start, stop
from StockBotApi import StockAlert
from Logger import logs
import json
import os
from td.credentials import TdCredentials
from td.client import TdAmeritradeClient
from datetime import datetime, timedelta
from time import sleep
import requests
import time
import yfinance as yf

from BackTesting import BackTest

class TDApi():
    def __init__(self, td_keys, paper_trading=False, starting_balance=100000, back_test=None):
        logs.debug("Creating TDApi object using " + td_keys)
        self.__td_keys = td_keys
        self.paper_trading = paper_trading
        self.starting_balance = starting_balance
        self.back_test : BackTest = back_test
        
        #Setup Authorization
        if not os.path.isfile(self.__td_keys):
            logs.info(self.__td_keys + " does not exist. Performing user Oauth!")
            os.makedirs(os.path.dirname(self.__td_keys), exist_ok=True)
            self.__client_id = input("Client ID: ")
            self.__redirect_url = input("Redirect Url: ")
            self.__td_credentials = TdCredentials(
                self.__client_id, 
                self.__redirect_url, 
                make_file=self.__td_keys)
            logs.debug(self.__td_keys + " succesfully created!")
        self.__json_dict = json.load(open(self.__td_keys))
        self.__td_credentials = TdCredentials(
            client_id=self.__json_dict["client_id"],
            redirect_uri=self.__json_dict["redirect_url"],
            credential_file=self.__td_keys
        )
        logs.debug(self.__td_keys + " succesfully loaded!")

        #Create TDAmeritrade API Objects
        logs.debug("Creating TDAmeritrade API Objects")
        self.td_client = TdAmeritradeClient(
            credentials=self.__td_credentials
        )
        self.options_service = self.td_client.options_chain()
        self.account_service = self.td_client.accounts()
        self.order_service = self.td_client.orders()
        logs.debug("TDAmeritrade API Objects Created")

        self.validate_key()

        self.stock_positions = []

    def create_order(self, stock_alert : StockAlert):
        order = StockOrder(stock_alert, self)
        for position in self.stock_positions:
            position : StockPosition
            if(position.stock_symbol==order.symbol):
                position.add_order(order)
                return order
        position = StockPosition(order.symbol, self, option=order.option)
        position.add_order(order)
        self.stock_positions.append(position)
        return order

    def create_orders(self, stock_alerts : list[StockAlert]):
        logs.debug("Creating Multiple stock orders from list")
        current_list = []
        for stock_alert in stock_alerts:
            current_list.append(self.create_order(stock_alert))
        return current_list

    def validate_key(self):
        logs.debug("Validating TD key")
        for i in range(5):
            try:
                logs.debug("Sending validation request")
                self.__td_credentials.validate_token()
                sleep(0.5)
                break
            except requests.HTTPError as e:
                logs.error("Failed to validate TD key")
    

class StockOrder():
    def __init__(self, stock_alert : StockAlert, td_api):
        logs.debug("Creating stock order from stock alert for:" + stock_alert.command + " " + stock_alert.stock)
        self.__stock_alert : StockAlert = stock_alert
        self.command = self.__stock_alert.command
        self.__td_api : TDApi = td_api
        self.option = False
        self.filled = False
        self.quantity = self.__stock_alert.quantity
        self.stock = False
        self.time = self.__stock_alert.time
        self.parent_position = None
        self.expiration_date = None
        if(self.__stock_alert.contract_type!=None):
            logs.debug("Stock alert is option alert")
            self.option = True
            if(self.__stock_alert.strike_price!=None):
                self.get_option_info(self.__stock_alert.stock, self.__stock_alert.contract_type, self.__stock_alert.strike_price)
        else:
            self.stock = True
            self.symbol = self.__stock_alert.stock

    def fill_order(self):
        logs.debug("Send stock buy order")
        if(self.__td_api.paper_trading):
            if(self.stock):
                if(self.command=="entry"):
                    stock_price = self.get_stock_price()
                    if(stock_price*self.quantity<self.__td_api.starting_balance):
                        self.__td_api.starting_balance-=(stock_price*self.quantity)
                        self.filled = True
                elif(self.command=="exit"):
                    stock_price = self.get_stock_price()
                    self.__td_api.starting_balance+=(stock_price*self.quantity)
                    self.filled = True
            elif(self.option):
                logs.debug("Paper trade options")


    def get_stock_price(self):
        # # diff = datetime(year=2016,month=5,day=1).date()-datetime(year=1964,month=2,day=1).date()
        # # start_in_millis=int(diff.total_seconds()*1000)
        # # start = datetime(year=self.__td_api.back_test.current_time.year,month=self.__td_api.back_test.current_time.month,day=self.__td_api.back_test.current_time.day)
        # print(self.__td_api.back_test.current_time)
        # data = yf.download(self.symbol,self.__td_api.back_test.current_time.date(),datetime.now().date(), interval="5m")
        # print(data)
        # # start = datetime(year=2022, month=2, day=1)
        # # epoch = datetime.utcfromtimestamp(0)
        # # #1648857540
        # # # print(epoch_time)
        # # # print(start)
        # # epoch_time = int((start - epoch).total_seconds() * 1000.0) - 60000
        # # print(epoch_time)

        # # if(self.__td_api.back_test):
        # #     price_history = self.__td_api.td_client.price_history().get_price_history(
        # #         symbol=self.symbol,
        # #         frequency_type='minute',
        # #         period_type="day",
        # #         frequency=1,
        # #         end_date=epoch_time,
        # #         start_date=epoch_time,
        # #         extended_hours_needed=True
        # #     )
        # #     print(price_history["candles"][-1])
        # #     # print(start_in_millis)
        # #     # print(epoch_time)
        return 100
        
    def set_parent_position(self, position):
        self.parent_position = position

    def get_option_info(self, ticker, contract_type, strike_price):
        logs.debug("Getting option info")
        start = self.__stock_alert.time - timedelta(days=self.__stock_alert.time.weekday())
        end = start + timedelta(days=4)
        self.expiration_date = end.strftime("%Y-%m-%d")
        option_chain_dict = {
            'symbol': ticker,
            'contractType': contract_type,
            'toDate': end.strftime("%Y-%m-%d"),
            'optionType': 'ALL',
            'range': 'NTM',
            'includeQuotes': True,
            'strike': strike_price
        }
        if(contract_type=="call"):
            ExpDateMap = "callExpDateMap"
        else:
            ExpDateMap = "putExpDateMap"
        option_chain = None
        for i in range(10):
            logs.debug("Making option service request")
            try:
                option_chain = self.__td_api.options_service.get_option_chain(option_chain_dict=option_chain_dict)
                sleep(0.5)
                break
            except requests.HTTPError as e:
                logs.error("Could not get option chain for: " + str(option_chain_dict))
        if(option_chain):
            if(option_chain["status"]=="SUCCESS"):
                logs.debug("Received option chain succesfully")
                expDate = list(option_chain[ExpDateMap].keys())[0]
                option = option_chain[ExpDateMap][expDate][str(float(strike_price))][0]
                self.option_info = option
                self.symbol = option["symbol"]
                self.last_price = option["last"]

class StockPosition():
    def __init__(self, stock_symbol, td_api, option=False, stock=False):
        logs.debug("Creating new stock position with symbol: " + stock_symbol)
        self.stock_symbol = stock_symbol
        self.option = option
        if(self.option):
            self.stock_name = self.stock_symbol.split("_")[0]
            self.stock_date = datetime.strptime(self.stock_symbol.split("_")[1][0:6], "%m%d%y")
            if(self.stock_symbol.split("_")[1][6]=="P"):
                self.contract_type="PUT"
            else:
                self.contract_type="CALL"
            self.strike_price = float(self.stock_symbol.split("_")[1][7:])
        self.stock_orders = []
        self.stock = stock
        self.__td_api :TDApi = td_api

    def __str__(self):
        return "Stock position " + self.stock_symbol

    def add_order(self, stock_order: StockOrder):
        logs.debug("Verifying stock matches symbol")
        if(stock_order.symbol==self.stock_symbol):
            logs.debug("Symbol matches adding order")
            self.stock_orders.append(stock_order)
            stock_order.set_parent_position(self)
        else:
            logs.debug("Stock does not match position symbol: " + self.stock_symbol)

    def update_position(self):
        if(self.option):
            option_chain_dict = {
                'symbol': self.stock_name,
                'contractType': self.contract_type,
                'toDate': self.stock_date.strftime("%Y-%m-%d"),
                'optionType': 'ALL',
                'range': 'NTM',
                'includeQuotes': True,
                'strike': self.strike_price
            }
            print(option_chain_dict)
            print(self.__td_api.options_service.get_option_chain(option_chain_dict = option_chain_dict))