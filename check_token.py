#!/usr/bin/env python

import sys, os, time, json
import requests

config = { 'API_KEY' : "",
           'OAUTH'   : "AMER.OAUTHAP",
           'HOST'    : "127.0.0.1",
           'PORT'    : 443 }

config_filename = "config.json"
if os.path.isfile(config_filename):
    config_file = open(config_filename)
    config = json.load(config_file)
    config_file.close()
else:
    print ("Unable to access '"+config_filename+"'")
    sys.exit(0)

tokens = { 'access_token' : None,
           'expires_in' : None,
           'token_type' : None,
           'refresh_token' : None,
           'refresh_token_expires_in' : None }

auth_filename = "tokens.json"
if os.path.isfile(auth_filename):
    try:
        token_file = open(auth_filename)
        tokens = json.load(token_file)
        token_file.close()
    except:
        print ("Unable to process '"+auth_filename+"'")
        sys.exit(1)

if time.time() > tokens['grant_time']+tokens['expires_in']:
    print("Token expired.")
    sys.exit(1)

headers = { 'Authorization' : tokens['token_type']+' '+tokens['access_token'] }
data = { 'apikey' : config['API_KEY'] }
apiReply = requests.get('https://api.tdameritrade.com/v1/marketdata/QQQ/quotes', headers=headers, data=data)

if apiReply.status_code == 200:
    quote = json.loads(apiReply.text)
    if not quote['QQQ']['delayed']:
        print("Token valid, realtime quotes detected.")
    else:
        print("Token valid, however quotes are delayed.")
else:
   print ('Error '+str(apiReply.status_code))
   print (apiReply.text)
