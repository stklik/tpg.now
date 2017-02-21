import json
import logging
from datetime import datetime
from urllib.request import urlopen

class ApiLimitException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class JSONError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Communicator(object):
    instance = None  # Singleton

    def __init__(self, maxConnectionTries=10, apiKey="xxx",
        baseURL="http://prod.ivtr-od.tpg.ch", apiVersion="v1",
        responseFormat="json", maxRequestsPerDay=5000):
        self.logger = logging.getLogger(__name__)

        self.maxConnectionTries = maxConnectionTries
        self.apiKey = apiKey
        self.baseURL = baseURL
        self.apiVersion = apiVersion
        self.responseFormat = responseFormat
        self.maxRequestsPerDay = maxRequestsPerDay
        self.currentCount = 0
        self.counterDate = datetime.today().date()

    @staticmethod
    def Instance():
        if not Communicator.instance:
            Communicator.instance = Communicator()
        return Communicator.instance

    def composeUrl(self, command, **kwargs):
        url = "/".join([self.baseURL,self.apiVersion])  # base url
        url += "/" + command  # add command
        url += "." + self.responseFormat  # attach format
        url += "?key=" + self.apiKey

        # add arguments
        for k,v in kwargs.items():
            url += "&" + k + "=" + v
        return url

    def sendRequest_getJSON(self, command, **kwargs):
        response = None
        tries = 0
        while tries < self.maxConnectionTries and not response:
            tries += 1
            try:
                textResponse = self.sendRequest(command, **kwargs)
                jsonResponse = json.loads(textResponse)
                return jsonResponse
            except json.JSONDecodeError:
                self.logger.error("Problem when parsing JSON response", exc_info=True)

        raise JSONError("Couldn't get parsable JSON after %s tries" % self.maxConnectionTries)

    def sendRequest(self, command, **kwargs):
        url = self.composeUrl(command, **kwargs)
        # response = urlopen(url).read()
        self.logger.info("Sending request to %s" % url)

        response = None
        tries = 0
        while tries < self.maxConnectionTries and not response:
            tries += 1
            try:
                response = urlopen(url).read()
            except ApiLimitException as e:  # forwarde exception if we have to many requests
                raise e
            except Exception:
                self.logger.debug("Exception during connection try")

                response = None
        if response:
            self.logger.info("Got a response after try #%s" % tries)
            return response.decode('utf-8')
        else:
            self.logger.error("No response after %s tries to contact the server" % tries)
            return None

    def sendRequest_withCounter(self, url):
        if self.counterDate != datetime.today().date():
            """ if today's date is not the counter date, update the date and reset the counter"""
            self.counterDate = datetime.today().date()
            self.currentCount = 0

        if self.currentCount < self.maxRequestsPerDay:
            self.currentCount += 1  # increase counter
            return urlopen(url).read()  # perform the request
        else:
            raise ApiLimitException("Maximum number of requests reached. Please contact @stklik !")
