import pytest
from tpgnow.communicator import Communicator
from tpgnow.arguments import Arguments
from config import Config

class TestFilter(object):

    @pytest.fixture
    def communicator_setup(self):
        Communicator.apiKey = Config.apiKey  # use real interface until we go live. But then we should mock it

    def test_station(self, communicator_setup):
        args = Arguments("CVIN/18/21").parse()
        assert args.stop.code == "CVIN"

    def test_oneLine(self, communicator_setup):
        args = Arguments("18").parse()
        assert "18" in [l.code for l in args.lines]

    def test_twoLines(self, communicator_setup):
        args = Arguments("CVIN/18/Y").parse()

        assert "18" in [l.code for l in args.lines]
        assert "Y" in [l.code for l in args.lines]

    def test_stationOnly(self, communicator_setup):
        args = Arguments("CVIN").parse()
        assert args.stop.code == "CVIN"

    def test_twoStations_chooseFirst(self, communicator_setup):
        args = Arguments("CVIN/18/BHET").parse()
        assert args.stop.code == "CVIN"

    stationNameData = [
        ("Tours Lignon",        "TLIG", "name with spaces"),
        ("Tourbillon",          "TOU0", "exact name"),
        ("tourbillon",          "TOU0", "ctalisation"),
        ("TOURBILLON",          "TOU0", "ctalisation"),
        ("Aéroport",            "AERO", "name with accent"),
        ("Sergy-Gare",          "SGGA", "name with dash"),
        ("SergyGare",           "SGGA", "forgot dash in name"),
        ("Val-d'Arve",          "VARV", "stop with apostrophy"),
        ("Chemin du Terraillet","CHTE", "spelt out Chemin"),
        ("Terraillet",          "CHTE", "omitted 'Ch. du'"),
        ("Pont de Lully",       "PLUL", "forget dashes"),
        ("Planpalais",          "PLPA", "missing character in name"),
        ("Plainbalais",         "PLPA", "wrong character in name"),
        ("Cornavin",            "CVIN", "substring reveals first string")
    ]
    @pytest.mark.parametrize("inString,expected,message", stationNameData)
    def test_stopNames(self, inString, expected, message, communicator_setup):
        args = Arguments(inString).parse()
        print(args.stop.normalizedName)
        assert args.stop.code == expected, message

    def test_compactArgument(self, communicator_setup):
        args = Arguments("COMPACT/CVIN/18/BHET").parse()
        assert args.compact == True

    def test_compactArgument_lowercaseWithSpaces(self, communicator_setup):
        args = Arguments(" compact /CVIN/18/BHET").parse()
        assert args.compact == True

    def test_timesArgument(self, communicator_setup):
        args = Arguments("TIMES/CVIN/18/BHET").parse()
        assert args.times == True

    def test_timesArgument_lowercaseWithSpaces(self, communicator_setup):
        args = Arguments(" times /CVIN/18/BHET").parse()
        assert args.times == True
