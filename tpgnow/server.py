from .arguments import Arguments
from .uiwriter import UiWriter, HtmlWriter, CLIFormatter, HtmlFormatter
from .tpg import Tpg
from config import Config

from datetime import datetime
from flask import render_template
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template

env = Environment(
    loader=FileSystemLoader("./templates"),
    undefined=DebugUndefined
)
env.filters['toHtml'] = HtmlWriter().toHtml


CLI_AGENTS = ['curl']

class Server(object):

    def getHelp(self, baseurl):
        template = env.get_template('help')
        return template.render(url=baseurl)

    def getInfo(self):
        stops = Tpg.getTodaysStops()
        lines = Tpg.getTodaysLines()

        template = env.get_template("info")
        rendered = template.render(stops=stops, lines=lines, timestamp=datetime.now())
        return rendered

    def getLineInfo(self):
        lines = Tpg.getTodaysLines()

        template = env.get_template("info")
        rendered = template.render(lines=lines, timestamp=datetime.now())
        return rendered

    def getStopInfo(self):
        stops = Tpg.getTodaysStops()

        template = env.get_template("info")
        rendered = template.render(stops=stops, timestamp=datetime.now())
        return rendered

    def getDepartures(self, argString):
        args = Arguments(argString).parse()
        stop, departures = Tpg.getNextDeparturesForStop(args)
        return UiWriter().writeDepartures(stop, departures, compact=args.compact, asTimes=args.times)


    def reply(self, response, agent):
        if any(name in agent for name in CLI_AGENTS):  # are we called from CLI
            formatting = CLIFormatter.getAsDict()

            # first pass: assemble
            template = env.get_template("base.cli")
            rendered = template.render(content=response)

            # second pass, format!
            formatTemp = Template(rendered)
            return formatTemp.render(**formatting)

        else:
            formatting = HtmlFormatter.getAsDict()
            template = env.get_template("base.html")
            rendered = template.render(content=response, google_analytics=Config().google_analytics)

            formatTemp = Template(rendered)
            return formatTemp.render(**formatting)
