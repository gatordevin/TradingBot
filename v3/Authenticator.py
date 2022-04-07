import os
from td.credentials import TdCredentials
import json

class Authenticator():
    def __init__(self, auth_dict : dict):
        self.__auth_dict : dict = auth_dict
        self.__auth_file : str = self.__auth_dict["auth_file"]
        os.makedirs(os.path.dirname(self.__auth_file), exist_ok=True)
        if not os.path.isfile(self.__auth_file):
            keys_list : list[str] = list(self.__auth_dict.keys())
            for key in keys_list:
                if key != "auth_file":
                    self.__auth_dict[key] = input(f"{key}: ")
            self.on_auth_create()
        else:
            self.__json_dict = json.load(open(self.__auth_dict["auth_file"]))
            for json_key in self.__json_dict:
                if json_key in self.__auth_dict:
                    self.__auth_dict[json_key] = self.__json_dict[json_key]
            self.on_auth_load(self.__auth_dict)

    def on_auth_create(self) -> None:
        return None

    def on_auth_load(self, auth_dict : dict) -> None:
        return auth_dict

class TDAuthenticator(Authenticator):
    def __init__(self, auth_file : str="config/td_credentials.json"):
        self.__auth_dict : dict = {
            "client_id" : "",
            "redirect_url" : "",
            "auth_file" : auth_file
        }
        super().__init__(self.__auth_dict)
        

    def on_auth_create(self) -> None:
        self.__td_credentials : TdCredentials = TdCredentials(
            self.__auth_dict["client_id"], 
            self.__auth_dict["redirect_url"], 
            make_file=self.__auth_dict["auth_file"]
        )

    def on_auth_load(self, auth_dict) -> None:
        self.__json_dict = json.load(open(self.__auth_dict["auth_file"]))
        self.__auth_dict["client_id"] = self.__json_dict["client_id"]
        self.__auth_dict["redirect_url"] = self.__json_dict["redirect_url"]
        self.__td_credentials : TdCredentials = TdCredentials(
            client_id=self.__auth_dict["client_id"],
            redirect_uri=self.__auth_dict["redirect_url"],
            credential_file=self.__auth_dict["auth_file"]
        )
        self.__td_credentials.validate_token()

    def get_credentials(self) -> TdCredentials: 
        return self.__td_credentials

class TwitterAuthenticator(Authenticator):
    def __init__(self, auth_file : str="config/twitter_credentials.json"):
        self.__auth_dict : dict = {
            "api_key" : "",
            "api_key_secret" : "",
            "bearer_token" : "",
            "access_token" : "",
            "access_token_secret" : "",
            "auth_file" : auth_file
        }
        super().__init__(self.__auth_dict)

    def on_auth_create(self) -> None:
        with open(self.__auth_dict["auth_file"], 'w') as auth_file:
            auth_file.write(json.dumps(self.__auth_dict))

    def on_auth_load(self, auth_dict) -> None:
        self.__auth_dict = auth_dict

    def get_twitter_keys(self) -> dict: 
        return self.__auth_dict

class DiscordAuthenticator(Authenticator):
    def __init__(self, auth_file : str="config/discord_credentials.json"):
        self.__auth_dict : dict = {
            "token" : "",
            "auth_file" : auth_file
        }
        super().__init__(self.__auth_dict)

    def on_auth_create(self) -> None:
        with open(self.__auth_dict["auth_file"], 'w') as auth_file:
            auth_file.write(json.dumps(self.__auth_dict))

    def on_auth_load(self, auth_dict) -> None:
        self.__auth_dict = auth_dict

    def get_token(self) -> str: 
        return self.__auth_dict["token"]

