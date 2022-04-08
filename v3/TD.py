from datetime import datetime
from turtle import position
from urllib.error import HTTPError
from td.client import TdAmeritradeClient
from td.rest.options_chain import OptionsChain
from Authenticator import TDAuthenticator
from time import sleep

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
        self.name : str = list(account_dict.keys())[0]
        self.__account_dict : dict = account_dict[self.name]
        self.type : str = self.__account_dict["type"]
        self.id : str = self.__account_dict["accountId"]
        self.day_trader : bool = self.__account_dict["isDayTrader"]
        self.positions : list[TDPosition] = self.get_positions()
        self.current_trading_balance : float = self.__account_dict["currentBalances"]["cashAvailableForTrading"]
        self.current_liquidation_value : float = self.__account_dict["currentBalances"]["liquidationValue"]
        self.initial_trading_balance : float = self.__account_dict["initialBalances"]["cashAvailableForTrading"]
        self.initial_account_value : float = self.__account_dict["initialBalances"]["accountValue"]
        self.time : datetime = datetime.now()

    def get_positions(self) -> list[TDPosition]:
        td_positions = [TDPosition(position) for position in self.__account_dict.get("positions", [])]
        return td_positions

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
        return print_string

class TDOptionParams():
    def __init__(
        self, 
        option_param_dict=None, 
        symbol=None,
        strike=None,
        from_date : datetime=None,
        to_date : datetime=None,
        contract_type=None,
        expiration_month=None,
        option_type="ALL",
        range="ALL",
        days_to_exp=None
    ):
        if not option_param_dict:
            self.__option_chain_dict = {
                'symbol': symbol,
                'strike': strike,
                'fromDate': from_date,
                'toDate': to_date,
                'contractType': contract_type,
                'expirationMonth': expiration_month,
                'optionType': option_type,
                'range': range,
                'daysToExpiration': days_to_exp
            }
        else:
            self.__option_chain_dict = option_param_dict
        self.time : datetime = datetime.now()
    def get_option_chain_dict(self):
        return self.__option_chain_dict

class TDOption():
    def __init__(self, option_dict : dict):
        self.__option_dict : dict = option_dict
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

    def __str__(self) -> str:
        print_string = f"Symbol: {self.symbol}\n"
        print_string += f"Strike Price: {self.strike_price}\n"
        print_string += f"Days to Expiration: {self.days_to_expiration}\n"
        print_string += f"Last Price: {self.last}\n"
        print_string += f"Time: {self.time}\n"
        return print_string


class TDOptionsChain():
    def __init__(self, options_chain_dict : dict, option_search_query : TDOptionParams):
        self.__options_chain_dict = options_chain_dict
        self.status : str = self.__options_chain_dict["status"]
        self.option_search_query = option_search_query
        self.options = []
        self.time : datetime = datetime.now()
        if(self.status=="SUCCESS"):
            self.symbol : str = self.__options_chain_dict["symbol"]
            self.interest_rate : float = self.__options_chain_dict["interestRate"]
            self.underlying_price : float = self.__options_chain_dict["underlyingPrice"]
            self.volatility : float = self.__options_chain_dict["volatility"]
            self.days_to_expiration : float = self.__options_chain_dict["daysToExpiration"]
            self.contract_number : int = self.__options_chain_dict["numberOfContracts"]
            self.options: list[TDOption] = self.get_options()
        else:
            print("FAILED: " + str(self.option_search_query))

    def get_options(self):
        td_options = []
        for option in self.__options_chain_dict["putExpDateMap"]:
            option_dict = self.__options_chain_dict["putExpDateMap"][option]
            for strike in option_dict.keys():
                strike_dict = option_dict[strike]
                for contract_dict in strike_dict:
                    td_option = TDOption(contract_dict)
                    td_options.append(td_option)
        for option in self.__options_chain_dict["callExpDateMap"]:
            option_dict = self.__options_chain_dict["callExpDateMap"][option]
            for strike in option_dict.keys():
                strike_dict = option_dict[strike]
                for contract_dict in strike_dict:
                    td_option = TDOption(contract_dict)
                    td_options.append(td_option)
        return td_options

    def __str__(self) -> str:
        print_string = f"Symbol: {self.symbol}\n"
        print_string += f"Status: {self.status}\n"
        print_string += f"Interest Rate: {self.interest_rate}\n"
        print_string += f"Underlying Price: {self.underlying_price}\n"
        print_string += f"Volatility: {self.volatility}\n"
        print_string += f"Days To Expiration: {self.days_to_expiration}\n"
        print_string += f"Number of contracts: {self.contract_number}\n"
        print_string += f"Time: {self.time}\n"
        print_string += f"Options: \n\n"
        for option in self.options:
            print_string += f"{option}\n"
        return print_string

class TDOrder():
    def __init__(self):
        self.order_dict = {}
    def get_order_dict(self) -> dict:
        return {}

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

class RecursiveTDOCOOrder():
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
                    "orderStrategyType": "TRIGGER",
                    "session": "NORMAL",
                    "duration": "GOOD_TILL_CANCEL",
                    "orderType": "LIMIT",
                    "price": self.limit_order_price,
                    "orderLegCollection": [
                        {
                        "instruction": "SELL_TO_OPEN",
                        "quantity": int(amount/2),
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
                        "price": self.limit_order_price*2,
                        "orderLegCollection": [
                            {
                            "instruction": "SELL_TO_OPEN",
                            "quantity": int(int(amount/2)/2),
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
                        "stopPrice": self.stop_order_price*2,
                        "orderLegCollection": [
                            {
                            "instruction": "SELL_TO_OPEN",
                            "quantity": int(amount/2),
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
    def __init__(self, auth_file="config/td_credentials.json", paper_trade_balance=0):
        self.__authenticator = TDAuthenticator(auth_file)
        self.__client = TdAmeritradeClient(
            credentials=self.__authenticator.get_credentials()
        )
        self.__options_service = self.__client.options_chain()
        self.__account_service = self.__client.accounts()
        self.__order_service = self.__client.orders()
        self.__stream_client = self.__client.streaming_api_client()
        self.__stream_services = self.__stream_client.services()
        self.__stream_services.quality_of_service(qos_level='0')

        self.__paper_trade_balance = paper_trade_balance
        self.__paper_trading = False
        if self.__paper_trade_balance:
            self.__paper_trading = True


    def get_accounts(self) -> list[TDAccount]:
        while True:
            try:
                td_accounts = []
                accounts = self.__account_service.get_accounts()
                for account in accounts:
                    if self.__paper_trading:
                        account_dict = account[list(account.keys())[0]]
                        account_dict["currentBalances"]["cashAvailableForTrading"] = self.__paper_trade_balance
                        account_dict["currentBalances"]["liquidationValue"] = self.__paper_trade_balance
                        account_dict["initialBalances"]["cashAvailableForTrading"] = self.__paper_trade_balance
                        account_dict["initialBalances"]["accountValue"] = self.__paper_trade_balance
                    td_accounts.append(TDAccount(account))
                return td_accounts
            except HTTPError:
                print("Failed to get accounts")
            sleep(1)

    def get_account_by_id(self, account_id : str) -> TDAccount:
        while True:
            try:
                accounts = self.__account_service.get_accounts()
                td_accounts = [TDAccount(account) for account in accounts]
                for td_account in td_accounts:
                    if td_account.id == account_id:
                        return td_account
                return None
            except HTTPError:
                print("Failed to get accounts")
            sleep(1)

    def get_options_chain(self, option_params : TDOptionParams) -> TDOptionsChain:
        while True:
            try:
                options_chain = self.__options_service.get_option_chain(option_chain_dict=option_params.get_option_chain_dict())
                td_options_chain = TDOptionsChain(options_chain, option_params)
                return td_options_chain
            except HTTPError:
                print("Failed to get options chain")
            sleep(1)

    def fill_order(self, td_order : TDOrder, td_account : TDAccount):
        while True:
            try:
                order = self.__order_service.place_order(account_id=td_account.id,order_dict=td_order.get_order_dict())
                return order
            except HTTPError:
                print("Failed to place order")
            sleep(1)
        return False