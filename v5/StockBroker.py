from TD import TDAccount, TDApi, TDSymbol

class StockBrokerSink():
    def __init__(self):
        super().__init__()
        self.sources = []

    def on_broker_sink(self, data : dict):
        pass

    def on_sink_add(self, source):
        self.sources.append(source)

class StockBrokerSource():
    def __init__(self):
        self.__broker_sinks : list[StockBrokerSink] = []
        super().__init__()

    def add_broker_sink(self, sink : StockBrokerSink):
        self.__broker_sinks.append(sink)
        sink.on_sink_add(self)

    def on_broker_source(self, data : dict):
        for sink in self.__broker_sinks:
            sink.on_broker_sink(data)

    def symbol_listen(self, symbol):
        pass

    def symbol_ignore(self, symbol):
        pass

class AccountChangeSink():
    def __init__(self):
        super().__init__()
        pass

    def on_account_sink(self, data : dict):
        pass

class AccountChangeSource():
    def __init__(self):
        self.__account_change_sinks : list[AccountChangeSink] = []
        super().__init__()

    def add_account_sink(self, sink : AccountChangeSink):
        self.__account_change_sinks.append(sink)

    def on_account_change_source(self, data : dict):
        for sink in self.__account_change_sinks:
            sink.on_account_sink(data)

class TDInfoSource(AccountChangeSource, StockBrokerSource):
    def __init__(self, account_name=None):
        super(TDInfoSource, self).__init__()
        self.__td_api : TDApi = TDApi.get_td_api()
        self.__td_account : TDAccount = self.__td_api.get_account(account_name)
        self.__td_account.add_account_listener(self)
    
    def on_account_change(self, account):
        self.on_account_change_source(account)

    def symbol_listen(self, symbol):
        symbol = self.__td_api.symbol_listen(symbol)
        symbol.add_symbol_listeners(self)
        return symbol

    def symbol_ignore(self, symbol):
        symbol = self.__td_api.symbol_ignore(symbol)

    def on_symbol_update(self, symbol : TDSymbol):
        self.on_broker_source(symbol)
