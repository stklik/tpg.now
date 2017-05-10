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

    def getHelp(self, **kwargs):
        template = env.get_template('help')
        return template.render(url=kwargs.get("baseurl", None))

    def getInfo(self, **kwargs):
        stops = Tpg.getTodaysStops()
        lines = Tpg.getTodaysLines()
        return UiWriter().info(stops=stops, lines=lines)

    def getLineInfo(self, **kwargs):
        lines = Tpg.getTodaysLines()
        return UiWriter().info(lines=lines)

    def getStopInfo(self, **kwargs):
        stops = Tpg.getTodaysStops()
        return UiWriter().info(stops=stops)

    def getDepartures(self, argString, **kwargs):
        args = Arguments(argString).parse()
        stop, departures = Tpg.getNextDeparturesForStop(args)
        return_html = not self.is_CLI_agent(kwargs.get("agent", None))
        url = kwargs.get("url", None)
        return UiWriter(html=return_html).writeDepartures(stop, departures, url=url, compact=args.compact, asTimes=args.times)


    def reply(self, response, **kwargs):
        if self.is_CLI_agent(kwargs.get("agent", None)):  # are we called from CLI
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

    def is_CLI_agent(self, agent):
        return any(name in agent for name in CLI_AGENTS)
