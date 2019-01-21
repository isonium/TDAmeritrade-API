#!/usr/bin/env python

# This will ask for your API Key the first time you run it and create a config.json
# It assumes an IP of 127.0.0.1 and PORT 443, but you can edit 'config.json' once created.
#
# You must first generate SSL certficates for the HTTPS server.
#
# openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
#
# The if you don't have tokens this is will open a browser for you to login into your account.
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

import sys
import os
import time
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, quote_plus
import requests
import ssl

if not os.path.isfile('certificate.pem') or not os.path.isfile('key.pem'):
    print("")
    print("You need to generate SSL certificates")
    print("")
    print("openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem")
    print("")
    sys.exit(1)

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
    config['API_KEY'] = input('Enter your API Key: ').strip()
    config_file = open(config_filename, 'w')
    config_file.write(json.dumps(config))
    config_file.close()       

redirect_uri = "https://"+config['HOST']
if config['PORT'] != 443: redirect_uri = redirect_uri+":"+str(config['PORT'])
client_id = config['API_KEY']+"@"+config['OAUTH']
redirect_uri_encoded = quote_plus(redirect_uri)

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
        pass

class TDAmeritradeHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    global write_tokens
    def write_tokens(authReplytext):
        response = json.loads(authReplytext)
        response.setdefault('error', [None])
        if response['error'][0] == None:
            tokens = json.loads(authReplytext)
            tokens['grant_time'] = int(time.time())
            token_file = open(auth_filename, 'w')
            token_file.write(json.dumps(tokens))
            token_file.close()       

    global update_tokens
    def update_tokens():
        global tokens
        global client_id
        global redirect_uri
        global auth_filename
        if time.time() > tokens['grant_time']+tokens['expires_in']/5*4:
            headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
            data = { 'grant_type': 'refresh_token', 'refresh_token': tokens['refresh_token'], 'access_type': 'offline', 'code': '', 'client_id': client_id, 'redirect_uri': redirect_uri }
            authReply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
            write_tokens(authReply.text)

    def do_GET(self):
        self._set_headers()
        path, _, query_string = self.path.partition('?')
        query = parse_qs(query_string)
        query.setdefault('code', [''])
        code = query['code'][0]

        #Post Access Token Request with new code
        if code != '':
            global tokens
            global client_id
            global redirect_uri
            headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
            data = { 'grant_type': 'authorization_code', 'access_type': 'offline', 'code': code, 'client_id': client_id, 'redirect_uri': redirect_uri }
            authReply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
            write_tokens(authReply.text)
            self.wfile.write(authReply.text.encode())

start_server = True
if tokens['access_token'] != None:
    update_tokens()
    temp = tokens
    temp.setdefault('error', [None])
    if temp['error'] == "invalid_grant":
        os.remove(auth_filename)
    else:
        start_server = False

if start_server:
    try:
        httpd = HTTPServer((config['HOST'], config['PORT']), TDAmeritradeHandler)
        httpd.socket = ssl.wrap_socket (httpd.socket, keyfile='key.pem', certfile='certificate.pem', server_side=True)
        webbrowser.open_new("https://auth.tdameritrade.com/auth?response_type=code&redirect_uri="+redirect_uri_encoded+"&client_id="+client_id)
        httpd.handle_request()
    except PermissionError:
        print("Unable to bind "+config['HOST']+":"+str(config['PORT'])+" with current permissions. (Try 'sudo ./tda-auth.py')")
        sys.exit(0)
    except:
        print("Unknown error.")
        sys.exit(0)

def forever():
    if tokens['access_token'] != None:
        update_tokens()
        temp = tokens
        temp.setdefault('error', [None])
        if temp['error'] == "invalid_grant":
            print ("Timer Abort: 'invalid_grant'")
            sys.exit(0)
        else:
            update_tokens()
            t = threading.Timer(tokens['expires_in']/20, forever)
            t.start()
            t.join()

if sys.argv[1] is not None:
    if sys.argv[1] == 'forever': forever()
