import json
from unittest.mock import patch, MagicMock
from tpgnow.communicator import Communicator
from tpgnow.tpg import Tpg

class TestTpg(object):

    def test_getLineColour_existingColourWorks(self):
        mockColours = """
{"timestamp":"2017-02-20T15:42:49+0100",
"colors":[
{"lineCode":"18","hexa":"cc3399","background":"cc3399","text":"FFFFFF"},
{"lineCode":"F","hexa":"FF9999","background":"FF9999","text":"000000"},
{"lineCode":"Y","hexa":"FF9999","background":"FF9999","text":"000000"},
{"lineCode":"Z","hexa":"FF9999","background":"FF9999","text":"000000"}]}
"""
        mock = Communicator()
        mock.sendRequest = MagicMock(return_value=mockColours)
        Communicator.instance = mock

        assert Tpg.getLineColor("Y")["background"] == "FF9999"
        assert Tpg.getLineColor("Y")["foreground"] == "000000"

    def test_getLineColour_nonExistingColour_returnsNone(self):
        mockColours = """
{"timestamp":"2017-02-20T15:42:49+0100",
"colors":[
{"lineCode":"18","hexa":"cc3399","background":"cc3399","text":"FFFFFF"},
{"lineCode":"F","hexa":"FF9999","background":"FF9999","text":"000000"},
{"lineCode":"Y","hexa":"FF9999","background":"FF9999","text":"000000"},
{"lineCode":"Z","hexa":"FF9999","background":"FF9999","text":"000000"}]}
"""
        mock = Communicator()
        mock.sendRequest = MagicMock(return_value=mockColours)
        Communicator.instance = mock

        assert Tpg.getLineColor("B") == None
