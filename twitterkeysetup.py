import sys
import configparser

config = configparser.ConfigParser(interpolation=None)
config.add_section('twitter')

config['twitter']['APIKey'] = sys.argv[1]
config['twitter']['APIKeySecret'] = sys.argv[2]
config['twitter']['BearerToken'] = sys.argv[3]
config['twitter']['AccessToken'] = sys.argv[4]
config['twitter']['AccessTokenSecret'] = sys.argv[5]

with open('twitterkeys.ini', 'w') as configfile:
    config.write(configfile)