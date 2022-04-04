from Logger import logs

class StockAlert():
    def __init__(self, command, stock, price, strike_price, contract_type, time, tweet, quantity=1):
        logs.debug("Creating stock alert object for: " + stock + " " + command)
        self.command = command
        self.stock = stock
        self.price = price
        self.quantity = quantity
        if(strike_price!=None):
            self.strike_price = float(strike_price)
        else:
            self.strike_price = None
        if(contract_type!=None):
            self.contract_type = contract_type.upper()
        else:
            self.contract_type = None
        self.time = time
        self.tweet = tweet