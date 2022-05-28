
import asyncio
from lib2to3.pgen2 import token
from threading import Thread
from time import sleep
from Authenticator import TDApiAuthenticator
from tda.streaming import StreamClient
from tda.client import Client
from datetime import datetime

class TDOrder():
    def __init__(self, order_dict : dict):
        self.__order_dict = order_dict
        self.session = self.__order_dict["session"]
        self.duration = self.__order_dict["duration"]
        self.order_leg_collection = self.__order_dict.get("orderLegCollection", [])
        self.symbol = self.order_leg_collection[0]["instrument"]["symbol"]
        if(self.order_leg_collection[0]["instrument"]["assetType"] == "EQUITY"):
            self.option_type = None
        else:
            self.option_type = self.order_leg_collection[0]["instrument"]["putCall"]
        self.order_type = self.__order_dict["orderType"]
        self.complex_order_strategy_type = self.__order_dict["complexOrderStrategyType"]
        self.quantity = self.__order_dict["quantity"]
        self.filled_quantity = self.__order_dict["filledQuantity"]
        self.remaining_quantity = self.__order_dict["remainingQuantity"]
        self.requested_destination = self.__order_dict["requestedDestination"]
        self.destination_link_name = self.__order_dict["destinationLinkName"]
        self.price = self.__order_dict.get("price", 0)
        if(self.price==0):
            self.price = self.__order_dict.get("stopPrice", 0)
        self.child_orders = self.get_child_orders()
        self.order_strategy_type = self.__order_dict["orderStrategyType"]
        self.id = self.__order_dict["orderId"]
        self.cancelable = self.__order_dict["cancelable"]
        self.editable = self.__order_dict["editable"]
        self.status = self.__order_dict["status"]
        self.entered_time = self.__order_dict["enteredTime"]
        self.close_time = self.__order_dict.get("closeTime", None)
        self.tag = self.__order_dict["tag"]
        self.account_id = self.__order_dict["accountId"]

    def get_child_orders(self) -> list:
        child_orders = []
        for order in self.__order_dict.get("childOrderStrategies", []):
            order : dict
            order_strategies = order.get("childOrderStrategies", [])
            for strategy in order_strategies:
                strategy : dict
                child_order = TDOrder(strategy)
                child_orders.append(child_order)
        return child_orders

    def get_order_dict(self) -> dict:
        return {}


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

class TDAccount():
    def __init__(self, account_dict : dict):
        self.set_values(account_dict)
        self.__account_change_listeners = []

    def add_account_listener(self, listener):
        self.__account_change_listeners.append(listener)
        listener.on_account_change(self)

    def set_values(self, account_dict):
        self.name : str = list(account_dict.keys())[0]
        self.__account_dict : dict = account_dict[self.name]
        self.type : str = self.__account_dict["type"]
        self.id : str = self.__account_dict["accountId"]
        self.day_trader : bool = self.__account_dict["isDayTrader"]
        self.positions : list[TDPosition] = self.get_positions()
        self.orders : list[TDOrder] = self.get_orders()
        self.current_trading_balance : float = self.__account_dict["currentBalances"]["cashAvailableForTrading"]
        self.current_liquidation_value : float = self.__account_dict["currentBalances"]["liquidationValue"]
        self.initial_trading_balance : float = self.__account_dict["initialBalances"]["cashAvailableForTrading"]
        self.initial_account_value : float = self.__account_dict["initialBalances"]["accountValue"]

    def on_account_info(self, account_info : dict):
        self.set_values(account_info)
        for listener in self.__account_change_listeners:
            listener.on_account_change(self)

    def get_positions(self) -> list[TDPosition]:
        td_positions = [TDPosition(position) for position in self.__account_dict.get("positions", [])]
        return td_positions

    def get_orders(self) -> list[TDOrder]:
        td_orders = [TDOrder(order) for order in self.__account_dict.get("orderStrategies", [])]
        return td_orders

class TDSymbol():
    def __init__(self, symbol_dict : dict, td_client, option=False):
        self.option = option
        self.__symbol_dict = symbol_dict
        self.__td_client = td_client

        self.symbol : str = None
        self.bid_price : float = None
        self.ask_price : float = None
        self.last_price : float = None
        self.bid_size : int = None
        self.ask_size : int = None
        self.high_price : float = None
        self.low_price : float = None
        self.open_price : float = None
        self.close_price : float = None
        self.volatility : float = None
        self.net_change : float = None

        self.__symbol_listeners = []
        if option:
            self.set_option(self.__symbol_dict)
        else:
            self.set_stock(self.__symbol_dict)

    def update_stock(self):
        stock_info = self.__td_client.get_quote(self.symbol).json()
        self.set_stock(stock_info)
        

    def set_stock(self, symbol_dict):
        self.__symbol_dict = symbol_dict[list(symbol_dict.keys())[0]]

        self.symbol = self.__symbol_dict["symbol"]
        self.cusip = self.__symbol_dict["cusip"]
        self.bid_price = self.__symbol_dict["bidPrice"]
        self.ask_price = self.__symbol_dict["askPrice"]
        self.last_price = self.__symbol_dict["lastPrice"]
        self.bid_size = self.__symbol_dict["bidSize"]
        self.ask_size = self.__symbol_dict["askSize"]
        self.ask_id = self.__symbol_dict["askId"]
        self.bid_id = self.__symbol_dict["bidId"]
        self.total_volume = self.__symbol_dict["totalVolume"]
        self.high_price = self.__symbol_dict["highPrice"]
        self.low_price = self.__symbol_dict["lowPrice"]
        self.close_price = self.__symbol_dict["closePrice"]
        self.volatility = self.__symbol_dict["volatility"]
        self.open_price = self.__symbol_dict["openPrice"]
        self.net_change = self.__symbol_dict["netChange"]
        self.pe_ratio = self.__symbol_dict["peRatio"]
        self.on_symbol_update()

    def update_stock(self, symbol_dict):
        self.__symbol_dict = symbol_dict
        self.symbol = self.__symbol_dict["key"]
        if self.__symbol_dict.get("BID_PRICE", None) is not None:
            self.bid_price = self.__symbol_dict["BID_PRICE"]
        if self.__symbol_dict.get("ASK_PRICE", None) is not None:
            self.ask_price = self.__symbol_dict["ASK_PRICE"]
        if self.__symbol_dict.get("LAST_PRICE", None) is not None:
            self.last_price = self.__symbol_dict["LAST_PRICE"]
        if self.__symbol_dict.get("BID_SIZE", None) is not None:
            self.bid_size = self.__symbol_dict["BID_SIZE"]
        if self.__symbol_dict.get("ASK_SIZE", None) is not None:
            self.ask_size = self.__symbol_dict["ASK_SIZE"]
        if self.__symbol_dict.get("ASK_ID", None) is not None:
            self.ask_id = self.__symbol_dict["ASK_ID"]
        if self.__symbol_dict.get("BID_ID", None) is not None:
            self.bid_id = self.__symbol_dict["BID_ID"]
        if self.__symbol_dict.get("TOTAL_VOLUME", None) is not None:
            self.total_volume = self.__symbol_dict["TOTAL_VOLUME"]
        if self.__symbol_dict.get("HIGH_PRICE", None) is not None:
            self.high_price = self.__symbol_dict["HIGH_PRICE"]
        if self.__symbol_dict.get("LOW_PRICE", None) is not None:
            self.low_price = self.__symbol_dict["LOW_PRICE"]
        if self.__symbol_dict.get("CLOSE_PRICE", None) is not None:
            self.close_price = self.__symbol_dict["CLOSE_PRICE"]
        if self.__symbol_dict.get("VOLATILITY", None) is not None:
            self.volatility = self.__symbol_dict["VOLATILITY"]
        if self.__symbol_dict.get("OPEN_PRICE", None) is not None:
            self.open_price = self.__symbol_dict["OPEN_PRICE"]
        if self.__symbol_dict.get("NET_CHANGE", None) is not None:
            self.net_change = self.__symbol_dict["NET_CHANGE"]
        if self.__symbol_dict.get("PE_RATIO", None) is not None:
            self.pe_ratio = self.__symbol_dict["PE_RATIO"]
        self.on_symbol_update()

    def update_option(self, symbol_dict):
        self.__symbol_dict = symbol_dict
        self.symbol = self.__symbol_dict["key"]
        if self.__symbol_dict.get("cusip", None) is not None:
            self.cusip = self.__symbol_dict["cusip"]
        if self.__symbol_dict.get("BID_PRICE", None) is not None:
            self.bid = self.__symbol_dict["BID_PRICE"]
        if self.__symbol_dict.get("ASK_PRICE", None) is not None:
            self.ask = self.__symbol_dict["ASK_PRICE"]
        if self.__symbol_dict.get("LAST_PRICE", None) is not None:
            self.last = self.__symbol_dict["LAST_PRICE"]
        if self.__symbol_dict.get("BID_SIZE", None) is not None:
            self.bid_size = self.__symbol_dict["BID_SIZE"]
        if self.__symbol_dict.get("ASK_SIZE", None) is not None:
            self.ask_size = self.__symbol_dict["ASK_SIZE"]
        if self.__symbol_dict.get("ASK_ID", None) is not None:
            self.ask_id = self.__symbol_dict["ASK_ID"]
        if self.__symbol_dict.get("BID_ID", None) is not None:
            self.bid_id = self.__symbol_dict["BID_ID"]
        if self.__symbol_dict.get("TOTAL_VOLUME", None) is not None:
            self.total_volume = self.__symbol_dict["TOTAL_VOLUME"]
        if self.__symbol_dict.get("HIGH_PRICE", None) is not None:
            self.high_price = self.__symbol_dict["HIGH_PRICE"]
        if self.__symbol_dict.get("LOW_PRICE", None) is not None:
            self.low_price = self.__symbol_dict["LOW_PRICE"]
        if self.__symbol_dict.get("CLOSE_PRICE", None) is not None:
            self.close_price = self.__symbol_dict["CLOSE_PRICE"]
        if self.__symbol_dict.get("VOLATILITY", None) is not None:
            self.volatility = self.__symbol_dict["VOLATILITY"]
        if self.__symbol_dict.get("OPEN_PRICE", None) is not None:
            self.open_price = self.__symbol_dict["OPEN_PRICE"]
        if self.__symbol_dict.get("NET_CHANGE", None) is not None:
            self.net_change = self.__symbol_dict["NET_CHANGE"]
        if self.__symbol_dict.get("PE_RATIO", None) is not None:
            self.pe_ratio = self.__symbol_dict["PE_RATIO"]
        self.on_symbol_update()

    def set_option(self, symbol_dict):
        self.__symbol_dict = symbol_dict
        self.strike_price = list(self.__symbol_dict.keys())[0]
        self.__symbol_dict = self.__symbol_dict[self.strike_price][0]
        self.contract_type : str = self.__symbol_dict["putCall"]
        
        self.description : str = self.__symbol_dict["description"]

        self.symbol : str = self.__symbol_dict["symbol"]
        self.bid_price : float = self.__symbol_dict["bid"]
        self.ask_price : float = self.__symbol_dict["ask"]
        self.last_price : float = self.__symbol_dict["last"]
        self.bid_size : int = self.__symbol_dict["bidSize"]
        self.ask_size : int = self.__symbol_dict["askSize"]
        self.high_price : float = self.__symbol_dict["highPrice"]
        self.low_price : float = self.__symbol_dict["lowPrice"]
        self.open_price : float = self.__symbol_dict["openPrice"]
        self.close_price : float = self.__symbol_dict["closePrice"]
        self.volatility : float = self.__symbol_dict["volatility"]
        self.net_change : float = self.__symbol_dict["netChange"]

        self.mark : float = self.__symbol_dict["mark"]
        
        
        self.total_volume : int = self.__symbol_dict["totalVolume"]
        
        
        self.delta : float = self.__symbol_dict["delta"]
        self.gamma : float = self.__symbol_dict["gamma"]
        self.theta : float = self.__symbol_dict["theta"]
        self.vega : float = self.__symbol_dict["vega"]
        self.rho : float = self.__symbol_dict["rho"]
        self.theoretical_option_value : float = self.__symbol_dict["theoreticalOptionValue"]
        self.theoretical_volatility : float = self.__symbol_dict["theoreticalVolatility"]
        self.strike_price : float = self.__symbol_dict["strikePrice"]
        self.expiration_date : int = self.__symbol_dict["expirationDate"]
        self.days_to_expiration : int = self.__symbol_dict["daysToExpiration"]
        self.multiplier : int = self.__symbol_dict["multiplier"]
        self.percent_change : float = self.__symbol_dict["percentChange"]
        self.mark_change : float = self.__symbol_dict["markChange"]
        self.mark_percent_change : float = self.__symbol_dict["markPercentChange"]
        self.intrinsic_value : float = self.__symbol_dict["intrinsicValue"]
        self.time : datetime = datetime.now()
        self.on_symbol_update()

    def on_symbol_update(self):
        for listener in self.__symbol_listeners:
            listener.on_symbol_update(self)

    def add_symbol_listeners(self, listener):
        listener.on_symbol_update(self)
        self.__symbol_listeners.append(listener)
class TDBaseOrder():
    def __init__(self):
        super().__init__()

    def get_order_dict(self):
        pass

class TDStockOrder(TDBaseOrder):
    def __init__(self, stock_symbol : TDSymbol, quantity : int, price):
        super().__init__()
        self.__stock_symbol = stock_symbol
        self.__quantity = quantity
        self.__price = price
        self.make_dict()

    def get_order_dict(self):
        return self.order_dict
    
    def make_dict(self):
        self.order_dict = {
        "orderType": "LIMIT",
        "session": "NORMAL",
        "price": str(round(self.__price,2)),
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
            "instruction": "Buy",
            "quantity": self.__quantity,
            "instrument": {
                "symbol": self.__stock_symbol.symbol,
                "assetType": "EQUITY"
            }
            }
        ]
        }

class TDApi():
    td_api = None
    def __init__(self, token_account_name : str = "securitiesAccount"):
        self.__auth : TDApiAuthenticator = TDApiAuthenticator()
        self.__account_listeners = []
        self.__symbols = []
        self.__td_client : Client = self.__auth.get_client()
        self.__accounts : list[TDAccount] = self.get_accounts()
        self.__token_account_name = token_account_name
        self.__stream_client = self.get_stream_client()
        if self.__stream_client:
            # print("stream client")
            loop = asyncio.get_event_loop()
            self.__stream_thread = Thread(target=asyncio.run, args=[self.stream_main()], daemon=True)
            self.__stream_thread.start()
            # print("stream thread started")
        else:
            # Also run this if outside market hours
            # Stop this once market hours are entered
            self.__request_thread = Thread(target=self.symbol_request_main, daemon=True)
            self.__request_thread.start()

    @staticmethod
    def get_td_api():
        if not TDApi.td_api:
            TDApi.td_api = TDApi()
        return TDApi.td_api

    def symbol_request_main(self):
        while True:
            for td_symbol in self.__symbols:
                td_symbol : TDSymbol
                if td_symbol.option:
                    pass
                    # Get option chain data
                else:
                    stock_info = self.__td_client.get_quote(td_symbol.symbol).json()
                    td_symbol.set_stock(stock_info)
                sleep(0.5)

    def is_symbol_option(self, symbol):
        if True in [char.isdigit() for char in symbol]:
            return True
        return False

    def symbol_listen(self, symbol):
        for td_symbol in self.__symbols:
            td_symbol : TDSymbol
            if td_symbol.symbol == symbol:
                return td_symbol
        if self.is_symbol_option(symbol):
            option = True
            # self.__td_client.get_option_chain() Get Option chain
        else:
            stock_info = self.__td_client.get_quote(symbol).json()
            td_symbol = TDSymbol(stock_info, self)
        
        self.__symbols.append(td_symbol)
        return td_symbol

    def symbol_ignore(self, symbol):
        symbol_temp = self.__symbols
        for td_symbol in symbol_temp:
            td_symbol : TDSymbol
            if td_symbol.symbol == symbol:
                self.__symbols.remove(td_symbol)
                return td_symbol

    def activity_handler(self, message):
        streaming_account = self.get_account()
        account_info = self.__td_client.get_account(streaming_account.id).json()
        self.on_account_info(account_info, streaming_account.id)

    def equity_handler(self, messages):
        for message in messages["content"]:
            for td_symbol in self.__symbols:
                td_symbol : TDSymbol
                if td_symbol.symbol==message["key"]:
                    td_symbol.update_stock(message)

    def options_handler(self, messages):
        for message in messages["content"]:
            for td_symbol in self.__symbols:
                td_symbol : TDSymbol
                if td_symbol.symbol==message["key"]:
                    td_symbol.update_option(message)

    async def stream_main(self):
        print("TD Stream started")
        await self.__stream_client.login()
        await self.__stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        self.__stream_client.add_account_activity_handler(self.activity_handler)
        self.__stream_client.add_level_one_equity_handler(self.equity_handler)
        self.__stream_client.add_level_one_option_handler(self.options_handler)
        await self.__stream_client.account_activity_sub()
        old_symbols = []
        while True:
            current_symbols = self.__symbols
            added_symbols = list(set(current_symbols) - set(old_symbols))
            removed_symbols = list(set(old_symbols) - set(current_symbols))
            old_symbols = current_symbols
            for symbol in added_symbols:
                symbol : TDSymbol
                if symbol.option:
                    await self.__stream_client.level_one_option_subs([symbol.symbol])
                else:
                    await self.__stream_client.level_one_equity_subs([symbol.symbol])

            for symbol in removed_symbols:
                symbol : TDSymbol
                if symbol.option:
                    await self.__stream_client.level_one_option_unsubs([symbol.symbol])
                else:
                    await self.__stream_client.level_one_equity_unsubs([symbol.symbol])
            await self.__stream_client.handle_message()

    def add_account_listener(self, account : TDAccount):
        self.__account_listeners.append(account)

    def on_account_info(self, account_dict : dict, account_id):
        for account in self.__accounts:
            if account.id == account_id:
                account.on_account_info(account_dict)
    
    def get_accounts(self) -> list[TDAccount]:
        td_accounts = []
        accounts_json = self.__td_client.get_accounts(fields=[Client.Account.Fields.ORDERS,Client.Account.Fields.POSITIONS]).json()
        for account in accounts_json:
            td_account = TDAccount(account)
            td_accounts.append(td_account)
            self.add_account_listener(td_account)
        return td_accounts

    def get_account(self, name=None):
        if name is None:
            name = self.__token_account_name
        for account in self.__accounts:
            if account.name == name:
                return account

    def get_symbol(self):
        pass

    def fill_order(self, td_order : TDBaseOrder, td_account : TDAccount):
        while True:
            try:
                order = self.__td_client.place_order(account_id=td_account.id,order_spec=td_order.get_order_dict())
                print(td_order.get_order_dict())
                return order
            except HTTPError:
                print("Failed to place order")
            sleep(1)

    def get_stream_client(self) -> StreamClient:
        for account in self.__accounts:
            account : TDAccount
            if account.name == self.__token_account_name:
                return StreamClient(self.__td_client, account_id=account.id)
        return None

