from Authenticator import AlpacaAuthenticator

class Alpaca():
    def __init__(self, alpaca_credentials_file="config/alpaca_credentials.json"):
        self.__alpaca_credentials_file = alpaca_credentials_file
        authenticator = AlpacaAuthenticator(auth_file=self.__alpaca_credentials_file)