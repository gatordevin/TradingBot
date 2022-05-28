
from datetime import datetime, timedelta
from math import floor
from Parsers import StockAlertInfo
from TD import TD, TDAccount, TDOTOCOOrder, TDOption, TDOrder, TDPosition, TDSingleOrder


class SGBot():
    def __init__(self, trading_strategy : dict, td_api : TD, td_account : TDAccount):
        self.trading_strategy : dict = trading_strategy
        self.td_api : TD = td_api
        self.td_account : TDAccount = td_account
        self.balance_limit = self.trading_strategy.get("balance_limit", float("inf"))
        self.trade_number_target = self.trading_strategy.get("trade_number_target", 1)
        self.trade_balance_limit = self.balance_limit/self.trade_number_target
        self.remaining_balance = self.balance_limit
        self.td_account.order_listener(self.on_order)

    def on_order(self, message):
        open_options = []
        for position in self.td_account.positions:
            position :TDPosition
            if position.asset_type=="OPTION":
                open_options.append(position)
        all_orders = []
        for order in self.td_account.orders:
            order : TDOrder
            all_orders.append(order)
            for order_leg in order.child_orders:
                order_leg : TDOrder
                all_orders.append(order_leg)

        uncovered_options = open_options
        for position in open_options:
            for order in all_orders:
                order : TDOrder
                if order.symbol == position.symbol:
                    uncovered_options.remove(position)
                    break

        for option in uncovered_options:
            option : TDPosition
            simple_order = TDSingleOrder(option.long_quantity, option.symbol, stop_price=option.average_price*(1+self.trading_strategy.get("stop_loss_percent", 0)))
            self.td_api.fill_order(simple_order, self.td_account)


    def test_scale(self):
        for order in self.td_account.orders:
            order : TDOrder
            print("Order")
            for order_leg in order.child_orders:
                print("Order Leg")
                order_leg : TDOrder
                print(order_leg.symbol)
                print(order_leg.status)
                print("")
        for position in self.td_account.positions:
            position :TDPosition
            print("Position")
            print(position.symbol)
            print(position.long_quantity)
        
    def place_order(self, alert : StockAlertInfo) -> TDOrder:
        if(alert.option):
            if not self.trading_strategy.get("trade_lottos", False) and alert.lotto:
                return None
            option : TDOption = self.td_account.get_option(alert.stock,alert.contract_type, alert.strike_price, days_to_expiration=7)
            
            orer_price_label = self.trading_strategy.get("order_price", "alert")
            if(orer_price_label=="alert"):
                order_price = alert.buy_price
            elif(orer_price_label=="ask"):
                order_price = option.ask
            else:
                order_price = option.last

            if(alert.alert_type == "entry"):
                if(self.trading_strategy.get("maximum_option_price", float("inf"))>order_price>self.trading_strategy.get("minimum_option_price", 0)):
                    total_option_price = option.multiplier*order_price+1
                    # self.td_account = self.td_api.get_account_by_id(self.td_account.id)
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
                        oco_order = TDOTOCOOrder(
                            price=order_price, 
                            amount=option_number, 
                            symbol=option.symbol, 
                            stop_order_percent=stop_limit, 
                            limit_order_percent=stop_loss,
                            sell_amount=floor(option_number*self.trading_strategy.get("scale_strategy",{}).get("scale_percentage",1.0))
                        )
                        order = self.td_api.fill_order(oco_order, self.td_account)
                        if order:
                            self.remaining_balance-=total_option_price*option_number
                            self.trade_balance_limit-=total_option_price*option_number
                        print("Made order")
                        return option, total_option_price
                    else:
                        return None
                else:
                    return None
            elif(alert.alert_type == "scale"):
                scale_strategy : dict = self.trading_strategy.get("scale_strategy", None)
                if scale_strategy is not None:
                    scale_percentage = scale_strategy.get("scale_percentage", 0.5)
                    scale_price = scale_strategy.get("scale_price", "bid")
                    symbol = option.symbol

                    symbol_position = None
                    for position in self.td_account.positions:
                        position :TDPosition
                        if symbol == position.symbol:
                            symbol_position : TDPosition = position
                    if symbol_position is not None:
                        stop_order = TDSingleOrder(symbol_position.long_quantity, symbol, stop_price=option.bid*(1+self.trading_strategy.get("stop_loss_percent", 0)))
                        limit_order = TDSingleOrder(floor(symbol_position.long_quantity*scale_percentage), symbol, limit_price=option.bid)
                        self.td_api.fill_order(stop_order, self.td_account)
                        limit_order = self.td_api.fill_order(limit_order, self.td_account)
                        all_orders = []
                        for order in self.td_account.orders:
                            order : TDOrder
                            all_orders.append(order)
                            for order_leg in order.child_orders:
                                order_leg : TDOrder
                                all_orders.append(order_leg)
                        for order in all_orders:
                            order : TDOrder
                            if(order.symbol==symbol):
                                if(order.status=="WORKING"):
                                    self.td_account.cancel_order(order.id)
                        return option, option.bid
                return None
            elif(alert.alert_type == "exit"):
                symbol = option.symbol
                symbol_position = None
                for position in self.td_account.positions:
                    position :TDPosition
                    if symbol == position.symbol:
                        symbol_position : TDPosition = position
                if symbol_position is not None:
                    limit_order = TDSingleOrder(symbol_position.long_quantity, symbol, limit_price=option.bid)
                    self.td_api.fill_order(stop_order, self.td_account)
                    all_orders = []
                    for order in self.td_account.orders:
                        order : TDOrder
                        all_orders.append(order)
                        for order_leg in order.child_orders:
                            order_leg : TDOrder
                            all_orders.append(order_leg)
                    for order in all_orders:
                        order : TDOrder
                        if(order.symbol==symbol):
                            if(order.status=="WORKING"):
                                self.td_account.cancel_order(order.id)
                    return option, option.bid

                return None
        return None