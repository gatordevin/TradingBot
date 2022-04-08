
from datetime import datetime, timedelta
from math import floor
from Parsers import StockAlertInfo
from TD import TD, RecursiveTDOCOOrder, TDAccount, TDOCOOrder, TDOption, TDOptionParams, TDOrder


class SGBot():
    def __init__(self, trading_strategy : dict, td_api : TD, td_account : TDAccount):
        self.trading_strategy : dict = trading_strategy
        self.td_api : TD = td_api
        self.td_account : TDAccount = td_account
        self.balance_limit = self.trading_strategy.get("balance_limit", float("inf"))
        self.trade_number_target = self.trading_strategy.get("trade_number_target", 1)
        self.trade_balance_limit = self.balance_limit/self.trade_number_target
        self.remaining_balance = self.balance_limit
        
    def place_order(self, alert : StockAlertInfo) -> TDOrder:
        if(alert.option):
            if not self.trading_strategy.get("trade_lottos", False) and alert.lotto:
                return None
            option_params = TDOptionParams(
                symbol=alert.stock,
                contract_type=alert.contract_type,
                option_type="SC",
                strike=alert.strike_price,
                days_to_exp=7
            )
            options_chain = self.td_api.get_options_chain(option_params)

            option = options_chain.options[0]
            
            orer_price_label = self.trading_strategy.get("order_price", "alert")
            if(orer_price_label=="alert"):
                order_price = alert.buy_price
            else:
                order_price = option.last

            if(alert.alert_type == "entry"):
                if(self.trading_strategy.get("maximum_option_price", float("inf"))>order_price>self.trading_strategy.get("minimum_option_price", 0)):
                    total_option_price = option.multiplier*order_price+1
                    self.td_account = self.td_api.get_account_by_id(self.td_account.id)
                    account_balance = self.td_account.current_trading_balance
                    lowest_balance = self.trade_balance_limit
                    if(self.remaining_balance<lowest_balance):
                        lowest_balance = self.remaining_balance
                    if self.trading_strategy.get("check_account_balance", True):
                        if(account_balance<lowest_balance):
                            lowest_balance = account_balance
                    if(total_option_price>lowest_balance):
                        return None
                    option_number = floor(lowest_balance/total_option_price)
                    max_contract_number = self.trading_strategy.get("max_number_of_contracts", float("inf"))
                    if option_number>max_contract_number:
                        option_number = max_contract_number
                    stop_loss = self.trading_strategy.get("stop_loss_percent", 0)
                    stop_limit = self.trading_strategy.get("stop_limit_percent", 0)
                    if stop_loss != 0 and stop_limit != 0:
                        oco_order = RecursiveTDOCOOrder(
                            price=order_price, 
                            amount=option_number, 
                            symbol=option.symbol, 
                            stop_order_percent=stop_limit, 
                            limit_order_percent=stop_loss
                        )
                        order = self.td_api.fill_order(oco_order, self.td_account)
                        if order:
                            self.remaining_balance-=total_option_price*option_number
                            self.trade_balance_limit-=total_option_price*option_number
                        print("Made order")
                        return order
                    else:
                        return None
                else:
                    return None
            elif(alert.alert_type == "scale"):
                return None
            elif(alert.alert_type == "exit"):
                return None
        return None