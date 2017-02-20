from tpgnow.communicator import Communicator
from tpgnow.model import Stop, Line, Departure
from tpgnow.cache import Cache


class Tpg(object):
    cacheTime = 3600
    cache = Cache.Instance()

    @staticmethod
    def getTodaysStops():
        return Tpg.getTodaysStopsAndLines()[0]

    @staticmethod
    def getTodaysLines():
        return Tpg.getTodaysStopsAndLines()[1]

    @staticmethod
    def getTodaysStopsAndLines():
        todaysStops = "todaysStops"
        todaysLines = "todaysLines"

        if Tpg.cache.has(todaysLines):
            return Tpg.cache.read(todaysStops), Tpg.cache.read(todaysLines)

        json = Communicator.Instance().sendRequest_getJSON("GetStops")
        stops = [Stop(s["stopCode"],s["stopName"]) for s in json["stops"]]

        lines = []
        for stop in json["stops"]:
            for connection in stop["connections"]:
                line = Line(connection["lineCode"], connection["destinationName"])
                if line not in lines:
                    lines.append(line)
        Tpg.cache.write(todaysStops, stops, delay=Tpg.cacheTime)  # cache for an hour
        Tpg.cache.write(todaysLines, lines, delay=Tpg.cacheTime)

        return stops,lines

    @staticmethod
    def getNextDeparturesForStop(args):
        ''' Returns Lines (code, destination) to departureTimes (in seconds) '''
        json = None
        if args.lines:
            json = Communicator.Instance().sendRequest_getJSON("GetNextDepartures", stopCode=args.stop.code, linesCode=",".join([l.code for l in args.lines]))
        else:
            json = Communicator.Instance().sendRequest_getJSON("GetNextDepartures", stopCode=args.stop.code)

        stop = Stop.fromJson(json["stop"])

        departures = [Departure.fromJson(dep) for dep in json["departures"]]
        departuresFiltered = [dep for dep in departures if dep]
        return stop, departuresFiltered

    @staticmethod
    def getLineColor(code):
        ''' Returns the colour of the specified line '''
        return Tpg.getLineColors().get(code, None)

    @staticmethod
    def getLineColors():
        ''' Returns a dictionary of {line: colour} '''
        json = Communicator.Instance().sendRequest_getJSON("GetLinesColors")

        linesToColors = dict()
        for color in json["colors"]:
            linesToColors[color["lineCode"]] = {
                "background": color["background"],
                "foreground": color["text"]
                }
        return linesToColors
