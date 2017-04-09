from flask import render_template
from datetime import datetime
from enum import Enum
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template

env = Environment(
    loader=FileSystemLoader("./templates"),
    undefined=DebugUndefined
)

""" This module is not my proudest work. It should be improved. """

class HtmlFormatter(Enum):
    """Formatting"""
    RESET = 0  # All attributes off
    BOLD = 1  # Bold on
    UNDERSCORE = 4  # Underscore (on monochrome display adapter only)
    BLINK = 5  # Blink on
    REVERSE_VIDEO = 7  # Reverse video on
    CONCEALED = 8  # Concealed on

    """Foreground colors"""
    BLACK = 30  # Black
    RED = 31  # Red
    GREEN = 32  # Green
    YELLOW = 33  # Yellow
    BLUE=  34 # Blue
    MAGENTA = 35  # Magenta
    CYAN = 36  # Cyan
    WHITE = 37  # White

    """Background colors"""
    BGBLACK = 40  # Black
    BGRED = 41  # Red
    BGGREEN = 42  # Green
    BGYELLOW = 43  # Yellow
    BGBLUE=  44 # Blue
    BGMAGENTA = 45  # Magenta
    BGCYAN = 46  # Cyan
    BGWHITE = 47  # White

    def __str__(self):
        return '<span class="{}">'.format(self.name)

    @classmethod
    def getAsDict(cls):
        kwargs = {name.lower(): str(member) for name,member in cls.__members__.items()}
        endKwargs = {"end"+name.lower(): "</span>" for name,member in cls.__members__.items()}
        kwargs.update(endKwargs)
        return kwargs

class CLIFormatter(Enum):
    """Formatting"""
    RESET = 0  # All attributes off
    BOLD = 1  # Bold on
    UNDERSCORE = 4  # Underscore (on monochrome display adapter only)
    BLINK = 5  # Blink on
    REVERSE_VIDEO = 7  # Reverse video on
    CONCEALED = 8  # Concealed on

    """Foreground colors"""
    BLACK = 30  # Black
    RED = 31  # Red
    GREEN = 32  # Green
    YELLOW = 33  # Yellow
    BLUE=  34 # Blue
    MAGENTA = 35  # Magenta
    CYAN = 36  # Cyan
    WHITE = 37  # White

    """Background colors"""
    BGBLACK = 40  # Black
    BGRED = 41  # Red
    BGGREEN = 42  # Green
    BGYELLOW = 43  # Yellow
    BGBLUE=  44 # Blue
    BGMAGENTA = 45  # Magenta
    BGCYAN = 46  # Cyan
    BGWHITE = 47  # White

    def __str__(self):
        return '\033[{0}m'.format(self.value)

    @classmethod
    def getAsDict(cls):
        kwargs = {name.lower(): str(member) for name,member in cls.__members__.items()}
        endKwargs = {"end"+name.lower(): str(cls.RESET) for name,member in cls.__members__.items()}
        kwargs.update(endKwargs)
        return kwargs

HOUR = 3600  # seconds

TPG_MESSAGE = "Source : transports publics genevois (TPG), état en date du {:{dfmt}}.".format(datetime.now(), dfmt='%d.%m.%Y')
MAX_DEPARTURES_SHOWN = 10

CLI_AGENTS = ['curl']  # to be extended


class UiWriter(object):

    """
    D E P A R T U R E S
    """
    def writeDepartures(self, stop, departures, compact=False, asTimes=False):
        template = env.get_template("departuresHead")
        intro = template.render(stop=stop, maxDepartures=MAX_DEPARTURES_SHOWN, TPG_disclaimer=TPG_MESSAGE, timestamp=datetime.now())

        nextDepartures = [dep for dep in departures if dep.waitingTime < 1*HOUR]#
        linesToDeps = {dep.line: [] for dep in nextDepartures}  # create dict
        for dep in nextDepartures:
            linesToDeps[dep.line].append(dep)

        lineinfo = ""
        if compact:
            template = env.get_template("departuresCompact")
            lineinfo = template.render(linesToDeps=linesToDeps, asTimes=asTimes, maxDepartures=MAX_DEPARTURES_SHOWN)
        else:
            lineinfo = self.writeDeparturesFancy(linesToDeps, asTimes)

        if not lineinfo.strip():
            lineinfo = "{{red}}No departures from this stop within the next hour !{{endred}}"

        return intro +"\n\n"+ lineinfo


    def writeDeparturesFancy(self, linesToDeps, asTimes=False):
        groupedByLineCode = {line.code : dict() for line, departures in linesToDeps.items()}
        for line, departures in linesToDeps.items():
            groupedByLineCode[line.code][line] = departures

        renderings = []
        for key in sorted(groupedByLineCode.keys()):
            template = env.get_template("departuresFancy")
            renderings.append(template.render(code=key, linesToDeps=groupedByLineCode[key], asTimes=asTimes, maxDepartures=MAX_DEPARTURES_SHOWN))

        return "\n".join(renderings)

class HtmlWriter(object):

    def toHtml(self, text):
        """ I hate this function """
        inCurlyBrackets = False
        content = ""
        for c in text:
            if c == "{":
                inCurlyBrackets = True
                content += c
            elif c == "}":
                inCurlyBrackets = False
                content += c
            elif inCurlyBrackets:
                content += c
            elif c == " ":
                content += " "
            elif c == "\n":
                content += "<br />"
            else:
                content += c
        return content
