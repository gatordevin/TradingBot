import sys
import configparser

config = configparser.ConfigParser(interpolation=None)
config.add_section('td')

config['td']['ClientId'] = sys.argv[1]
config['td']['RedirectUri'] = sys.argv[2]
config['td']['AuthorizationCode'] = sys.argv[3]
config['td']['AccessToken'] = sys.argv[4]
config['td']['RefreshToken'] = sys.argv[5]

with open('tdkeys.ini', 'w') as configfile:
    config.write(configfile)