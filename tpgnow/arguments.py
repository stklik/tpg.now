from .tpg import Tpg
from .model import Stop, Line
import Levenshtein


class Arguments(object):

    compact = False
    times = False
    stop = None
    lines = []

    def __init__(self, argString):
        self.argString = argString

    def parse(self):
        # split by slashes
        candidates = self.argString.split("/")

        for candidate in candidates:
            if candidate.strip().upper() == "COMPACT":
                self.compact = True
            elif candidate.strip().upper() == "TIMES":
                self.times = True
            else:
                parsed = self.getCorrectArgument(candidate)
                if isinstance(parsed, Stop) and not self.stop:
                    self.stop = parsed
                elif isinstance(parsed, Line) and parsed not in self.lines:
                    self.lines.append(parsed)

        return self

    def getCorrectArgument(self, candidate):
        if candidate in [line.code for line in Tpg.getTodaysLines()]:
            return {line.code: line for line in Tpg.getTodaysLines()}.get(candidate)
        else:
            return self.getStopFromString(candidate)

    def getStopFromString(self, candidate):
        normalizedCandidate = Stop.normalizeStopName(candidate)
        if not Tpg.getTodaysStops():
            return None

        for stop in Tpg.getTodaysStops():
            if candidate.upper() == stop.code:
                return stop

            if normalizedCandidate == stop.normalizedName:
                return stop

        for stop in Tpg.getTodaysStops():
            if normalizedCandidate in stop.normalizedName:
                return stop

        # calculate the Levenshtein distance to all stop names
        codeToLevenshtein = {stop: Levenshtein.distance(
            normalizedCandidate, stop.normalizedName) for stop in Tpg.getTodaysStops()}
        # smallest Levenshtein distance
        minimum = min(codeToLevenshtein, key=codeToLevenshtein.get)
        return minimum
