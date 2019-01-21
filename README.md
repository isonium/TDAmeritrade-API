# TDAmeritrade-API
# Python 3 OATH Authentication for TD Ameritrade's API
#
# This will ask for your API Key the first time you run it and create a config.json
# It assumes an IP of 127.0.0.1 and PORT 443, but you can edit 'config.json' once created.
#
# You must first generate SSL certficates for the HTTPS server.
#
# openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
#
# The if you don't have tokens this will open a browser for you to login into your account.
# TD Ameritrade will pass the tokens back to the local HTTPS Server via your browser.
# It's normal to get a security warning from your browser, just accept the certficate you created.
# The tokens will be saved in 'tokens.json'
#
# Running again will use the refresh token in auth.json to get new tokens if less than
# six minutes remain.
#
# You will not need to login again unless your refresh token is expired or is invalidated.
#
# To keep your tokens.json file updated will valid tokens run.
#
# ./authenticate.py forever 
#
# The code is not the best, but it works.
#
# Visit TD Ameritrade's developer website for more information.
#
# https://developer.tdameritrade.com/content/getting-started
# Use https://127.0.0.1 as your callback URL.
#
# Code based on example code here.
# https://developer.tdameritrade.com/content/web-server-authentication-python-3
#
# On systems that restrict port < 1024 you may need to use 'sudo ./athenticate.py' or equivalent. 
#
# Requires sys, os, time, json, threading, webbrowser, http.server, urllib.parse, requests, and ssl modules.
#
