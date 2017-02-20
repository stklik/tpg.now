import logging
from datetime import datetime
import re
import traceback
from natsort import natsorted
from unidecode import unidecode
import re

class Departure(object):

    line = None
    timestamp = None
    waitingTime = None ## will be in seconds

    def __init__(self, line, timestamp, waitingTime):
        self.logger = logging.getLogger(__name__)

        self.line = line
        self.timestamp = timestamp
        self.waitingTime = waitingTime


    def __lt__(self, another):
        return self.waitingTime < another.waitingTime

    def formattedTime(self, asDepartureTime=False):
        if asDepartureTime:
            return self.formattedDepartureTime()
        else:
            return self.formattedWaitingTime()

    def formattedWaitingTime(self):
        m, s = divmod(int(self.waitingTime), 60)
        h, m = divmod(m, 60)

        if h > 0:
            return "%sh %smin" % (h,m)
        elif m > 0:
            return "{:2}min".format(m)
        else:
            return "{:2}sec".format(s)

    def formattedDepartureTime(self):
        return self.timestamp.strftime("%H:%M")

    @staticmethod
    def fromJson(jsonDeparture):
        try:
            line = Line(jsonDeparture["line"]["lineCode"],jsonDeparture["line"]["destinationName"])
            timestampText = jsonDeparture["timestamp"]
            conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', timestampText)
            timestamp = datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S%f%z" )  # e.g. 2017-01-26T20:55:31+0100
            wait = int(abs(int(jsonDeparture["waitingTimeMillis"]))/1000)
            return Departure(line, timestamp, wait)
        except KeyError:
            # print("Error, couldn't parse this departure:")
            # print(jsonDeparture)
            pass
        except:
            logger.error("Unknown error during creation of Departure from JSON", exc_info=True)
            return None



class Line(object):
    code = None
    destination = None

    def __init__(self, code, destination):
        self.code = code
        self.destination = destination

    def __eq__(self, another):
        return hasattr(another, 'code') and self.code == another.code

    def __hash__(self):
        return hash(self.code) ^ hash(self.destination)

    def __str__(self):
        return "{:>2} ─> {}".format(self.code, self.destination)

    def __lt__(self, another):
        return self.code == natsorted([self.code, another.code])[0]


class Stop(object):
    code = None
    name = None
    normalizedName = None

    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.normalizedName = Stop.normalizeStopName(name)

    def __eq__(self, another):
        return hasattr(another, 'code') and self.code == another.code

    def __hash__(self):
        return hash(self.code) ^ hash(self.name)

    def __lt__(self, another):
        return self.name < another.name

    def __str__(self):
        return "({}) {}".format(self.code, self.name)

    @staticmethod
    def normalizeStopName(name):
        upper = name.upper()
        unidecoded = unidecode(upper)
        onlyCharacters = re.sub(r'[^a-zA-Z]+', '', unidecoded)
        return onlyCharacters

    @staticmethod
    def fromJson(json):
        return Stop(json["stopCode"], json["stopName"])
