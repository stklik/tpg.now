import os
import logging
from flask import Flask, request, redirect

from config import Config
from tpgnow.server import Server
from tpgnow.communicator import Communicator

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
app.debug = True

# setup Communicator
Communicator.Instance().apiKey = os.getenv("API_KEY", Config.apiKey)

server = Server()

@app.route('/help')
def help():
    baseurl = request.headers.get('Host')
    response = server.getHelp(baseurl)
    agent = request.headers.get('User-Agent')
    return server.reply(response, agent)

@app.route('/info')
def info():
    response = server.getInfo()
    agent = request.headers.get('User-Agent')
    return server.reply(response, agent)

@app.route('/info/lines')
def infoLines():
    response = server.getLineInfo()
    agent = request.headers.get('User-Agent')
    return server.reply(response, agent)

@app.route('/info/stops')
def infoStops():
    response = server.getStopInfo()
    agent = request.headers.get('User-Agent')
    return server.reply(response, agent)

@app.route('/<path:path>')
def filtered(path):
    response = server.getDepartures(path)
    agent = request.headers.get('User-Agent')
    return server.reply(response, agent)

@app.route('/')
def home():
    return help()

if __name__ == "__main__":
    app.run(debug=True)
