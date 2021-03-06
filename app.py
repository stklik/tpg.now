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

def _get_agent_and_baseurl(request):
    agent = request.headers.get('User-Agent')
    baseurl = request.headers.get('Host')
    url = request.url
    print(url)
    return {"agent" : agent, "baseurl": baseurl, "url": url}

@app.route('/help')
def help():
    requestArgs = _get_agent_and_baseurl(request)
    response = server.getHelp(**requestArgs)
    return server.reply(response, **requestArgs)

@app.route('/info')
@app.route('/info/')
@app.route('/info/<path>')
def info(path=None):
    requestArgs = _get_agent_and_baseurl(request)
    response = ""
    if path == "stops":
        "fetching"
        response = server.getStopInfo(**requestArgs)
    elif path == "lines":
        response = server.getLineInfo(**requestArgs)
    else:
        response = server.getInfo(**requestArgs)
    return server.reply(response, **requestArgs)

@app.route('/<path:path>')
def filtered(path):
    requestArgs = _get_agent_and_baseurl(request)
    response = server.getDepartures(path, **requestArgs)
    return server.reply(response, **requestArgs)

@app.route('/')
def home():
    return help()

if __name__ == "__main__":
    app.run(debug=False)
