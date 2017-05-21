from flask import render_template
from datetime import datetime
from enum import Enum
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template
from tpgnow.singletable import SingleTableUnescaped

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

    def __init__(self, html=False):
        self.html = html

    def info(self, stops=None, lines=None):
        now = datetime.now()
        head = "tpg.now information\n%s\n" % now.strftime('%A %d.%m.%Y - %H:%M') + \
               "Source : transports publics genevois (TPG)" + \
               ", état en date du %s" % now.strftime('%d.%m.%Y')

        linesText = ""
        if lines:
            data = [[line.code for line in sorted(lines)[i:i + 15]]
                        for i in range(0, len(lines), 15)]
            table = SingleTableUnescaped(data)
            table.inner_heading_row_border = False
            table.inner_row_border = False
            table.outer_border = False
            linesText = "\n\nToday's operated lines are:\n\n"+table.table

        stopsText = ""
        if stops:
            data = [[str(stop) for stop in sorted(stops)[i:i + 4]]
                        for i in range(0, len(stops), 4)]

            data.insert(0, ["(CODE) Stopname"]*4)
            table = SingleTableUnescaped(data)
            table.inner_heading_row_border = True
            table.inner_row_border = False
            table.outer_border = False
            table.column_widths = [27]*4

            tableText = table.table
            if self.html:
                print("a")
                for stop in stops:
                    tableText = tableText.replace(str(stop),
                        "<a href='/%s' class='no_decoration'>%s</a>" % (stop.code, "{}".format(str(stop))))
                print("b")

            stopsText = "\n\nToday's operated stops are:\n\n"+tableText

        return head + linesText + stopsText


    """
    D E P A R T U R E S
    """
    def writeDepartures(self, stop, departures, compact=False, asTimes=False, url=None):
        template = env.get_template("departuresHead")
        intro = template.render(stop=stop, maxDepartures=MAX_DEPARTURES_SHOWN, TPG_disclaimer=TPG_MESSAGE, timestamp=datetime.now())

        nextDepartures = [dep for dep in departures if dep.waitingTime < 1*HOUR]#
        linesToDeps = {dep.line: [] for dep in nextDepartures}  # create dict
        for dep in nextDepartures:
            linesToDeps[dep.line].append(dep)

        lineinfo = ""
        if compact:
            data = [
                [str(line), " ".join([dep.formattedTime(asTimes) for dep in deps[:MAX_DEPARTURES_SHOWN]])]
                 for line, deps in linesToDeps.items()]
            table = SingleTableUnescaped(data)
            table.inner_heading_row_border = False
            table.inner_row_border = True
            table.column_widths = [23,93]
            lineinfo = table.table

        else:
            lineinfo = self.writeDeparturesFancy(linesToDeps, asTimes)

        if not lineinfo.strip():
            lineinfo = "{{red}}No departures from this stop within the next hour !{{endred}}"

        change_to_other = ""
        if self.html:
            if asTimes:
                link_url = url.replace("/times", "")
                change_to_other += """<p><a href='%s'>Display as waiting times</a></p>""" % link_url
            else:
                link_url = url.lstrip("/") + "/times"
                change_to_other += """<p><a href='%s'>Display as waiting times</a></p>""" % link_url

        return intro +"\n\n"+ change_to_other + lineinfo


    def writeDeparturesFancy(self, linesToDeps, asTimes=False):
        groupedByLineCode = {line.code : dict() for line, departures in linesToDeps.items()}
        for line, departures in linesToDeps.items():
            groupedByLineCode[line.code][line] = departures

        renderings = []
        for key in sorted(groupedByLineCode.keys()):
            data = [
                [str(line.destination), " ".join([dep.formattedTime(asTimes) for dep in deps[:MAX_DEPARTURES_SHOWN]])]
                 for line, deps in groupedByLineCode[key].items()]

            table = SingleTableUnescaped(data, title=key)
            table.inner_heading_row_border = False
            table.column_widths = [23,93]
            renderings.append(table.table)


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
