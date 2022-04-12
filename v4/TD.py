from requests import HTTPError
from Authenticator import TDApiAuthenticator
from tda import client
from tda.streaming import StreamClient
from tda.client import Client
import tda.client
from datetime import datetime, timedelta
from threading import Thread
from time import monotonic, sleep
import asyncio
import xmltodict
import json
from PaperTrader import PaperTrader

class TDOrderLeg():
    def __init__(self, order_leg_dict : dict):
        self.__order_leg_dict = order_leg_dict
        self.order_leg_type = self.__order_leg_dict["orderLegType"]
        self.leg_id = self.__order_leg_dict["legId"]
        self.asset_type = self.__order_leg_dict["instrument"]["assetType"]
        self.cusip = self.__order_leg_dict["instrument"]["cusip"]
        self.symbol = self.__order_leg_dict["instrument"]["symbol"]
        self.instruction = self.__order_leg_dict["instruction"]
        self.position_effect = self.__order_leg_dict["positionEffect"]
        self.quantity = self.__order_leg_dict["quantity"]

    def __str__(self) -> str:
        print_string = f"Asset Type: {self.asset_type}\n"
        print_string += f"Symbol: {self.symbol}\n"
        print_string += f"Instruction: {self.instruction}\n"
        print_string += f"Position Effect: {self.position_effect}\n"
        print_string += f"Quantity: {self.quantity}\n"
        return print_string

class TDOrder():
    def __init__(self, order_dict : dict):
        self.__order_dict = order_dict
        self.session = self.__order_dict["session"]
        self.duration = self.__order_dict["duration"]
        self.order_type = self.__order_dict["orderType"]
        self.complex_order_strategy_type = self.__order_dict["complexOrderStrategyType"]
        self.quantity = self.__order_dict["quantity"]
        self.filled_quantity = self.__order_dict["filledQuantity"]
        self.remaining_quantity = self.__order_dict["remainingQuantity"]
        self.requested_destination = self.__order_dict["requestedDestination"]
        self.destination_link_name = self.__order_dict["destinationLinkName"]
        self.price = self.__order_dict["price"]
        self.order_legs = self.get_order_leg()
        self.order_strategy_type = self.__order_dict["orderStrategyType"]
        self.id = self.__order_dict["orderId"]
        self.cancelable = self.__order_dict["cancelable"]
        self.editable = self.__order_dict["editable"]
        self.status = self.__order_dict["status"]
        self.entered_time = self.__order_dict["enteredTime"]
        self.close_time = self.__order_dict.get("closeTime", None)
        self.tag = self.__order_dict["tag"]
        self.account_id = self.__order_dict["accountId"]

    def get_order_leg(self) -> list[TDOrderLeg]:
        order_legs = [TDOrderLeg(order_leg) for order_leg in self.__order_dict.get("orderLegCollection", [])]
        return order_legs

    def __str__(self) -> str:
        print_string = f"Order Type: {self.order_type}\n"
        print_string += f"Quantity: {self.quantity}\n"
        print_string += f"Filled Quantity: {self.filled_quantity}\n"
        print_string += f"Remaining Quantity: {self.remaining_quantity}\n"
        print_string += f"Order Strategy Type: {self.order_strategy_type}\n"
        print_string += f"Order Id: {self.id}\n"
        print_string += f"Cancellable: {self.cancelable}\n"
        print_string += f"Status: {self.status}\n"
        print_string += f"Entered Time: {self.entered_time}\n"
        print_string += f"Close Time: {self.close_time}\n"
        print_string += f"Order Leg: \n\n"
        for order_leg in self.order_legs:
            print_string += f"Leg {order_leg}\n"
        return print_string


class TDPosition():
    def __init__(self, position_dict : dict):
        self.__position_dict : dict = position_dict
        self.average_price : float = self.__position_dict["averagePrice"]
        self.long_quantity : float = self.__position_dict["longQuantity"]
        self.asset_type : str = self.__position_dict["instrument"]["assetType"]
        self.cusip : str = self.__position_dict["instrument"]["cusip"]
        self.symbol : str = self.__position_dict["instrument"]["symbol"]
        self.market_value : float = self.__position_dict["marketValue"]
        self.time : datetime = datetime.now()
    
    def __str__(self) -> str:
        print_string = f"Symbol: {self.symbol}\n"
        print_string += f"Asset: {self.asset_type}\n"
        print_string += f"Quantity: {self.long_quantity}\n"
        print_string += f"Market value: {self.market_value}\n"
        print_string += f"Average Price: {self.average_price}\n"
        print_string += f"Cusip: {self.cusip}\n"
        print_string += f"Time: {self.time}\n"
        return print_string

class TDStock():
    def __init__(self, stock_dict : dict):
        self.__stock_dict = stock_dict[list(stock_dict.keys())[0]]
        self.symbol = self.__stock_dict["symbol"]
        self.cusip = self.__stock_dict["cusip"]
        self.bid_price = self.__stock_dict["bidPrice"]
        self.ask_price = self.__stock_dict["askPrice"]
        self.last_price = self.__stock_dict["lastPrice"]
        self.bid_size = self.__stock_dict["bidSize"]
        self.ask_size = self.__stock_dict["askSize"]
        self.ask_id = self.__stock_dict["askId"]
        self.bid_id = self.__stock_dict["bidId"]
        self.total_volume = self.__stock_dict["totalVolume"]
        self.high_price = self.__stock_dict["highPrice"]
        self.low_price = self.__stock_dict["lowPrice"]
        self.close_price = self.__stock_dict["closePrice"]
        self.volatility = self.__stock_dict["volatility"]
        self.open_price = self.__stock_dict["openPrice"]
        self.net_change = self.__stock_dict["netChange"]
        self.pe_ratio = self.__stock_dict["peRatio"]

    def set_values(self, stock_dict):
        self.__stock_dict = stock_dict
        self.symbol = self.__stock_dict["key"]
        if self.__stock_dict.get("BID_PRICE", None) is not None:
            self.bid_price = self.__stock_dict["BID_PRICE"]
        if self.__stock_dict.get("ASK_PRICE", None) is not None:
            self.ask_price = self.__stock_dict["ASK_PRICE"]
        if self.__stock_dict.get("LAST_PRICE", None) is not None:
            self.last_price = self.__stock_dict["LAST_PRICE"]
        if self.__stock_dict.get("BID_SIZE", None) is not None:
            self.bid_size = self.__stock_dict["BID_SIZE"]
        if self.__stock_dict.get("ASK_SIZE", None) is not None:
            self.ask_size = self.__stock_dict["ASK_SIZE"]
        if self.__stock_dict.get("ASK_ID", None) is not None:
            self.ask_id = self.__stock_dict["ASK_ID"]
        if self.__stock_dict.get("BID_ID", None) is not None:
            self.bid_id = self.__stock_dict["BID_ID"]
        if self.__stock_dict.get("TOTAL_VOLUME", None) is not None:
            self.total_volume = self.__stock_dict["TOTAL_VOLUME"]
        if self.__stock_dict.get("HIGH_PRICE", None) is not None:
            self.high_price = self.__stock_dict["HIGH_PRICE"]
        if self.__stock_dict.get("LOW_PRICE", None) is not None:
            self.low_price = self.__stock_dict["LOW_PRICE"]
        if self.__stock_dict.get("CLOSE_PRICE", None) is not None:
            self.close_price = self.__stock_dict["CLOSE_PRICE"]
        if self.__stock_dict.get("VOLATILITY", None) is not None:
            self.volatility = self.__stock_dict["VOLATILITY"]
        if self.__stock_dict.get("OPEN_PRICE", None) is not None:
            self.open_price = self.__stock_dict["OPEN_PRICE"]
        if self.__stock_dict.get("NET_CHANGE", None) is not None:
            self.net_change = self.__stock_dict["NET_CHANGE"]
        if self.__stock_dict.get("PE_RATIO", None) is not None:
            self.pe_ratio = self.__stock_dict["PE_RATIO"]

    def on_stock_change(self, data):
        sleep(0.1)
        self.set_values(data)

class TDOption():
    def __init__(self, stock_dict : dict):
        self.__option_dict = stock_dict
        self.strike_price = list(self.__option_dict.keys())[0]
        self.__option_dict = self.__option_dict[self.strike_price][0]
        self.contract_type : str = self.__option_dict["putCall"]
        self.symbol : str = self.__option_dict["symbol"]
        self.description : str = self.__option_dict["description"]
        self.bid : float = self.__option_dict["bid"]
        self.ask : float = self.__option_dict["ask"]
        self.last : float = self.__option_dict["last"]
        self.mark : float = self.__option_dict["mark"]
        self.bid_size : int = self.__option_dict["bidSize"]
        self.ask_size : int = self.__option_dict["askSize"]
        self.high_price : float = self.__option_dict["highPrice"]
        self.low_price : float = self.__option_dict["lowPrice"]
        self.open_price : float = self.__option_dict["openPrice"]
        self.close_price : float = self.__option_dict["closePrice"]
        self.total_volume : int = self.__option_dict["totalVolume"]
        self.net_change : float = self.__option_dict["netChange"]
        self.volatility : float = self.__option_dict["volatility"]
        self.delta : float = self.__option_dict["delta"]
        self.gamma : float = self.__option_dict["gamma"]
        self.theta : float = self.__option_dict["theta"]
        self.vega : float = self.__option_dict["vega"]
        self.rho : float = self.__option_dict["rho"]
        self.theoretical_option_value : float = self.__option_dict["theoreticalOptionValue"]
        self.theoretical_volatility : float = self.__option_dict["theoreticalVolatility"]
        self.strike_price : float = self.__option_dict["strikePrice"]
        self.expiration_date : int = self.__option_dict["expirationDate"]
        self.days_to_expiration : int = self.__option_dict["daysToExpiration"]
        self.multiplier : int = self.__option_dict["multiplier"]
        self.percent_change : float = self.__option_dict["percentChange"]
        self.mark_change : float = self.__option_dict["markChange"]
        self.mark_percent_change : float = self.__option_dict["markPercentChange"]
        self.intrinsic_value : float = self.__option_dict["intrinsicValue"]
        self.time : datetime = datetime.now()

    def set_values(self, stock_dict):
        # print(stock_dict)
        self.__stock_dict = stock_dict
        self.symbol = self.__stock_dict["key"]
        if self.__stock_dict.get("cusip", None) is not None:
            self.cusip = self.__stock_dict["cusip"]
        if self.__stock_dict.get("BID_PRICE", None) is not None:
            self.bid = self.__stock_dict["BID_PRICE"]
        if self.__stock_dict.get("ASK_PRICE", None) is not None:
            self.ask = self.__stock_dict["ASK_PRICE"]
        if self.__stock_dict.get("LAST_PRICE", None) is not None:
            self.last = self.__stock_dict["LAST_PRICE"]
        if self.__stock_dict.get("BID_SIZE", None) is not None:
            self.bid_size = self.__stock_dict["BID_SIZE"]
        if self.__stock_dict.get("ASK_SIZE", None) is not None:
            self.ask_size = self.__stock_dict["ASK_SIZE"]
        if self.__stock_dict.get("ASK_ID", None) is not None:
            self.ask_id = self.__stock_dict["ASK_ID"]
        if self.__stock_dict.get("BID_ID", None) is not None:
            self.bid_id = self.__stock_dict["BID_ID"]
        if self.__stock_dict.get("TOTAL_VOLUME", None) is not None:
            self.total_volume = self.__stock_dict["TOTAL_VOLUME"]
        if self.__stock_dict.get("HIGH_PRICE", None) is not None:
            self.high_price = self.__stock_dict["HIGH_PRICE"]
        if self.__stock_dict.get("LOW_PRICE", None) is not None:
            self.low_price = self.__stock_dict["LOW_PRICE"]
        if self.__stock_dict.get("CLOSE_PRICE", None) is not None:
            self.close_price = self.__stock_dict["CLOSE_PRICE"]
        if self.__stock_dict.get("VOLATILITY", None) is not None:
            self.volatility = self.__stock_dict["VOLATILITY"]
        if self.__stock_dict.get("OPEN_PRICE", None) is not None:
            self.open_price = self.__stock_dict["OPEN_PRICE"]
        if self.__stock_dict.get("NET_CHANGE", None) is not None:
            self.net_change = self.__stock_dict["NET_CHANGE"]
        if self.__stock_dict.get("PE_RATIO", None) is not None:
            self.pe_ratio = self.__stock_dict["PE_RATIO"]

    def on_option_change(self, data):
        self.set_values(data)

    def __str__(self) -> str:
        print_string = f"Symbol: {self.symbol}\n"
        print_string += f"Strike Price: {self.strike_price}\n"
        print_string += f"Days to Expiration: {self.days_to_expiration}\n"
        print_string += f"Last Price: {self.last}\n"
        print_string += f"Time: {self.time}\n"
        return print_string
    
class TDAccount():
    def __init__(self, account_dict : dict, td_client : client.Client, id=None, paper_account=None):
        self.__td_client : client.Client = td_client
        self.__id = id
        self.__paper_acount : PaperTrader = paper_account
        self.set_values(account_dict)

        self.time : datetime = datetime.now()

        self.stream_client : StreamClient = StreamClient(self.__td_client, account_id=self.id)

        # loop = asyncio.get_event_loop()
        self.__listener_thread = Thread(target=asyncio.run, args=[self.main_thread()])
        # self.__handler_thread = Thread(target=asyncio.run,args=[self.run_streaming_handler())
        # loop.create_task(self.run_streaming_handler())
        # self.__handler_thread.daemon = True
        # self.__handler_thread.start()
        self.__listener_thread.daemon = True
        self.__listener_thread.start()

        self.__order_listeners = set()
        self.order_listener(self.on_order)

        self.__stock_listeners = set()
        self.__option_listeners = set()

        self.__stock_alerts = []
        self.__option_alerts = []

        self.__td_stocks : list[TDStock] = []

        self.__stock_alert_size = 0
        self.__option_alert_size = 0

    def stock_listener(self, listener):
        self.__stock_listeners.add(listener)

    def option_listener(self, listener):
        self.__option_listeners.add(listener)

    def equity_handler(self, messages):
        # print("equity change")
        for message in messages["content"]:
            for stock in self.__stock_listeners:
                stock : TDStock
                if stock.symbol==message["key"]:
                    stock.on_stock_change(message)

    def options_handler(self, messages):
        # print("option change")
        for message in messages["content"]:
            for option in self.__option_listeners:
                option : TDOption
                if option.symbol==message["key"]:
                    option.on_option_change(message)

    def order_listener(self, listener):
        self.__order_listeners.add(listener)

    def on_order(self, order_data):
        self.update_account()

    def get_positions(self) -> list[TDPosition]:
        td_positions = [TDPosition(position) for position in self.__account_dict.get("positions", [])]
        return td_positions

    def update_account(self) -> dict:
        if(self.__id==None):
            account_dict = self.__td_client.get_account(self.id, fields=[Client.Account.Fields.ORDERS,Client.Account.Fields.POSITIONS]).json()
        else:
            account_dict = self.__paper_acount.get_account()[0]
        self.set_values(account_dict)

    def get_orders(self) -> list[TDOrder]:
        td_orders = [TDOrder(order) for order in self.__account_dict.get("orderStrategies", [])]
        return td_orders

    def set_values(self, account_dict):
        self.name : str = list(account_dict.keys())[0]
        self.__account_dict : dict = account_dict[self.name]
        self.type : str = self.__account_dict["type"]
        if(self.__id==None):
            self.id : str = self.__account_dict["accountId"]
        else:
            self.id = self.__id
        self.day_trader : bool = self.__account_dict["isDayTrader"]
        self.positions : list[TDPosition] = self.get_positions()
        self.orders : list[TDOrder] = self.get_orders()
        self.current_trading_balance : float = self.__account_dict["currentBalances"]["cashAvailableForTrading"]
        self.current_liquidation_value : float = self.__account_dict["currentBalances"]["liquidationValue"]
        self.initial_trading_balance : float = self.__account_dict["initialBalances"]["cashAvailableForTrading"]
        self.initial_account_value : float = self.__account_dict["initialBalances"]["accountValue"]

    def get_stock(self, stock):
        self.__stock_alerts.append(stock)
        stock = TDStock(self.__td_client.get_quote(stock).json())
        self.stock_listener(stock)
        return stock

    def get_option(self, symbol, contract_type, strike_price, days_to_expiration):
        option_dict = self.__td_client.get_option_chain(symbol,contract_type=Client.Options.ContractType(contract_type), days_to_expiration=days_to_expiration,option_type=Client.Options.Type.STANDARD,strategy=Client.Options.Strategy.ANALYTICAL, strike=strike_price, from_date=datetime.now()+timedelta(days=days_to_expiration-7), to_date=datetime.now()+timedelta(days=days_to_expiration)).json()
        td_options = []
        if contract_type == "CALL":
            call_map = option_dict["callExpDateMap"]
            for date in call_map.keys():
                option = TDOption(call_map[date])
                self.__option_alerts.append(option.symbol)
                td_options.append(option)
                self.option_listener(option)
        elif contract_type == "PUT":
            put_map = option_dict["putExpDateMap"]
            for date in put_map.keys():
                option = TDOption(put_map[date])
                self.__option_alerts.append(option.symbol)
                td_options.append(option)
                self.option_listener(option)
        return td_options[0]

    async def main_thread(self):
        await self.stream_client.login()
        await self.listener()
        

    async def listener(self):
        
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        self.stream_client.add_account_activity_handler(self.activity_handler)
        self.stream_client.add_level_one_equity_handler(self.equity_handler)
        self.stream_client.add_level_one_option_handler(self.options_handler)
        await self.stream_client.account_activity_sub()
        while True:
            await self.stream_client.handle_message()
            if len(self.__stock_alerts)>self.__stock_alert_size:
                for stock_alert in list(self.__stock_alerts)[self.__stock_alert_size:]:
                    await self.stream_client.level_one_equity_subs([stock_alert])
                    print("alerting stock: " + stock_alert)
                self.__stock_alert_size = len(self.__stock_alerts)
            elif len(self.__option_alerts)>self.__option_alert_size:
                for option_alert in list(self.__option_alerts)[self.__option_alert_size:]:
                    await self.stream_client.level_one_option_subs([option_alert])
                    print("alerting option: " + option_alert)
                self.__option_alert_size = len(self.__option_alerts)

    async def run_streaming_handler(self):
        while True:
            await self.stream_client.handle_message()
        #     await self.stream_client.handle_message()


    def activity_handler(self, messages):
        if(self.__id==None):
            for message in messages["content"]:
                message_type : str = message["MESSAGE_TYPE"]
                message_data : str = message["MESSAGE_DATA"]
                if(message_type == "SUBSCRIBED"):
                    print("Account stream activated for: " + self.id)
                else:
                    if(message_data != ""):
                        data_dict = json.loads(json.dumps(xmltodict.parse(message_data)))
                        for listener in self.__order_listeners:
                            listener(data_dict)
                    
    def __str__(self) -> str:
        print_string = f"Name: {self.name}\n"
        print_string += f"Type: {self.type}\n"
        print_string += f"ID: {self.id}\n"
        print_string += f"Day Trader: {self.day_trader}\n"
        print_string += f"Current Trading Balance: {self.current_trading_balance}\n"
        print_string += f"Current Liquidation Value: {self.current_liquidation_value}\n"
        print_string += f"Initial trading Balance: {self.initial_trading_balance}\n"
        print_string += f"Initial Account Value: {self.initial_account_value}\n"
        print_string += f"Time: {self.time}\n"
        print_string += f"Positions: \n\n"
        for position in self.positions:
            print_string += f"Positions: {position}\n"
        print_string += f"Orders: \n\n"
        for order in self.orders:
            print_string += f"Orders: {order}\n"
        return print_string

class TDOCOOrder():
    def __init__(self, price, amount, symbol, stop_order_percent, limit_order_percent):
        super().__init__()
        self.price : float = price
        self.amount : int = amount
        self.symbol : str = symbol
        self.stop_order_percent : float = stop_order_percent
        self.limit_order_percent : float = limit_order_percent
        self.stop_order_price : float = round(price*(1-stop_order_percent),2)
        self.limit_order_price : float = round(price*(1-limit_order_percent),2)
        self.time : datetime = datetime.now()
        self.order_dict : dict={
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
                    "symbol": symbol
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
                    "price": self.limit_order_price,
                    "orderLegCollection": [
                        {
                        "instruction": "SELL_TO_OPEN",
                        "quantity": amount,
                        "instrument": {
                            "assetType": "OPTION",
                            "symbol": symbol
                        }
                        }
                    ]
                    },
                    {
                    "orderStrategyType": "SINGLE",
                    "session": "NORMAL",
                    "duration": "GOOD_TILL_CANCEL",
                    "orderType": "STOP",
                    "stopPrice": self.stop_order_price,
                    "orderLegCollection": [
                        {
                        "instruction": "SELL_TO_OPEN",
                        "quantity": amount,
                        "instrument": {
                            "assetType": "OPTION",
                            "symbol": symbol 
                        }
                        }
                    ]
                    }
                ]
                }
            ]
            }
    def get_order_dict(self) -> dict:
        return self.order_dict

class TD():
    def __init__(self, authenticator_path : str="config/td_api_credentials.json", account_type : str="securitiesAccount", paper_trading_file=None):
        self.__auth : TDApiAuthenticator = TDApiAuthenticator(authenticator_path)
        self.__td_client : client.Client = self.__auth.get_client()

        self.__paper_trading_file = paper_trading_file
        if(self.__paper_trading_file!=None):
            self.__paper_trader = PaperTrader(self.__paper_trading_file)
        self.__paper_trading = self.__paper_trading_file is not None

        self.accounts = self.get_accounts()

    def fill_order(self, td_order : TDOrder, td_account : TDAccount):
        while True:
            try:
                if self.__paper_trading:
                    order = self.__paper_trader.fill_order(td_order)
                else:
                    order = self.__td_client.place_order(account_id=td_account.id,order_spec=td_order.get_order_dict())
                return order
            except HTTPError:
                print("Failed to place order")
            sleep(1)

    def activity_handler(self, messages):
        for message in messages["content"]:
            message_type : str = message["MESSAGE_TYPE"]
            message_data : str = message["MESSAGE_DATA"]
            if(message_type == "SUBSCRIBED"):
                print("Account stream activated for: " + self.id)
            else:
                if(message_data != ""):
                    data_dict = json.loads(json.dumps(xmltodict.parse(message_data)))
                    for listener in self.__order_listeners:
                        listener(data_dict)

    def get_accounts(self) -> list[TDAccount]:
        td_accounts = []
        if(self.__paper_trading):
            accounts_json = self.__td_client.get_accounts(fields=[Client.Account.Fields.ORDERS,Client.Account.Fields.POSITIONS]).json()
            # td_account = TDAccount(accounts_json[0], self.__td_client)
            # self.stream_client = td_account.stream_client
            
            account_dict : dict = accounts_json[0]["securitiesAccount"]
            id : str = account_dict["accountId"]

            accounts_json = self.__paper_trader.get_account()
            for account in accounts_json:
                td_account = TDAccount(account, self.__td_client, id=id, paper_account=self.__paper_trader)
                self.stream_client = td_account.stream_client
                td_accounts.append(td_account)
        else:
            accounts_json = self.__td_client.get_accounts(fields=[Client.Account.Fields.ORDERS,Client.Account.Fields.POSITIONS]).json()
            streamer = True
            for account in accounts_json:
                td_account = TDAccount(account, self.__td_client)
                td_accounts.append(td_account)
                self.stream_client = td_account.stream_client
                streamer = False
        
        return td_accounts


        