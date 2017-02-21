import pytest
from unittest.mock import patch
from tpgnow.model import Stop, Line
from tpgnow.arguments import Arguments
import logging

logging.basicConfig(level=logging.DEBUG)

class TestFilter(object):

    @classmethod
    def setup_class(cls):

        stops = [ Stop("TLIG", "Tours Lignon"), Stop("TOU0", "Tourbillon"),
                Stop("CHTE", "Ch. du Terraillet"), Stop("PLPA", "Plainpalais"),
                Stop("CVIN", "Gare Cornavin"), Stop("AERO", "Aéroport"),
                Stop("SGGA", "Sergy-Gare"), Stop("VARV", "Val-d'Arve"),
                Stop("PLUL", "Pont-de-Lully"), Stop("BHET", "Bachet-de-Pesay") ]

        lines = [ Line("1", "somewhere"), Line("55", "somewhere"),
                Line("4", "somewhere"), Line("18", "somewhere"),
                Line("Y", "somewhere") ]

        TestFilter.patcher = patch("tpgnow.arguments.Tpg")
        TestFilter.tpg_mock = TestFilter.patcher.start()
        TestFilter.tpg_mock.getTodaysStops.return_value = stops
        TestFilter.tpg_mock.getTodaysLines.return_value = lines

    @classmethod
    def teardown_class(cls):
        TestFilter.patcher.stop()

    def test_station(self):
        args = Arguments("CVIN/18/21").parse()
        assert args.stop.code == "CVIN"

    def test_oneLine(self):
        args = Arguments("18").parse()
        assert "18" in [l.code for l in args.lines]

    def test_twoLines(self):
        args = Arguments("CVIN/18/Y").parse()

        assert "18" in [l.code for l in args.lines]
        assert "Y" in [l.code for l in args.lines]

    def test_stationOnly(self):
        args = Arguments("CVIN").parse()
        assert args.stop.code == "CVIN"

    def test_twoStations_chooseFirst(self):
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
    def test_stopNames(self, inString, expected, message):
        args = Arguments(inString).parse()
        assert args.stop.code == expected, message

    def test_compactArgument(self):
        args = Arguments("COMPACT/CVIN/18/BHET").parse()
        assert args.compact == True

    def test_compactArgument_lowercaseWithSpaces(self):
        args = Arguments(" compact /CVIN/18/BHET").parse()
        assert args.compact == True

    def test_timesArgument(self):
        args = Arguments("TIMES/CVIN/18/BHET").parse()
        assert args.times == True

    def test_timesArgument_lowercaseWithSpaces(self):
        args = Arguments(" times /CVIN/18/BHET").parse()
        assert args.times == True
