import os
import json

class PaperTrader():
    def __init__(self, paper_trading_file="trading/test.json"):
        self.paper_trading_file = paper_trading_file
        os.makedirs(os.path.dirname(self.paper_trading_file), exist_ok=True)
        if not os.path.isfile(self.paper_trading_file):
            self.account_dict = self.create_new_account()
            print(self.account_dict)
            with open(self.paper_trading_file, 'w') as auth_file:
                json.dump(self.account_dict, auth_file)
        else:
            with open(self.paper_trading_file, 'r') as auth_file:
                self.account_dict = json.load(auth_file)

    def create_new_account(self) -> dict:
        account_dict = {}
        account_dict["paperAccount"] = {}
        account_dict["paperAccount"]["type"] = "CASH"
        account_dict["paperAccount"]["accountId"] = "123456789"
        account_dict["paperAccount"]["roundTrips"] = 0
        account_dict["paperAccount"]["isDayTrader"] = False
        account_dict["paperAccount"]["isClosingOnlyRestricted"] = False
        account_dict["paperAccount"]["positions"] = []
        account_dict["paperAccount"]["orderStrategies"] = []
        account_dict["paperAccount"]["initialBalances"] = {}
        account_dict["paperAccount"]["initialBalances"]["accruedInterest"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["cashAvailableForTrading"] = 100000
        account_dict["paperAccount"]["initialBalances"]["cashAvailableForWithdrawal"] = 100000
        account_dict["paperAccount"]["initialBalances"]["cashBalance"] = 100000
        account_dict["paperAccount"]["initialBalances"]["bondValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["cashReceipts"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["liquidationValue"] = 100000
        account_dict["paperAccount"]["initialBalances"]["longOptionMarketValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["longStockValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["moneyMarketFund"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["mutualFundValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["shortOptionMarketValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["shortStockValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["isInCall"] = False
        account_dict["paperAccount"]["initialBalances"]["unsettledCash"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["cashDebitCallValue"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["pendingDeposits"] = 0.0
        account_dict["paperAccount"]["initialBalances"]["accountValue"] = 100000
        account_dict["paperAccount"]["currentBalances"] = {}
        account_dict["paperAccount"]["currentBalances"]["accruedInterest"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["cashBalance"] = 100000
        account_dict["paperAccount"]["currentBalances"]["cashReceipts"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["longOptionMarketValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["liquidationValue"] = 100000
        account_dict["paperAccount"]["currentBalances"]["longMarketValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["moneyMarketFund"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["savings"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["shortMarketValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["pendingDeposits"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["cashAvailableForTrading"] = 100000
        account_dict["paperAccount"]["currentBalances"]["cashAvailableForWithdrawal"] = 100000
        account_dict["paperAccount"]["currentBalances"]["cashCall"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["longNonMarginableMarketValue"] = 100000
        account_dict["paperAccount"]["currentBalances"]["totalCash"] = 100000
        account_dict["paperAccount"]["currentBalances"]["shortOptionMarketValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["mutualFundValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["bondValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["cashDebitCallValue"] = 0.0
        account_dict["paperAccount"]["currentBalances"]["unsettledCash"] = 0.0
        account_dict["paperAccount"]["projectedBalances"] = {}
        account_dict["paperAccount"]["projectedBalances"]["cashAvailableForTrading"] = 100000
        account_dict["paperAccount"]["projectedBalances"]["cashAvailableForWithdrawal"] = 100000
        return account_dict

        

    def get_account(self):
        return [self.account_dict]