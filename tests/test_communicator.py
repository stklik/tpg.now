import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from tpgnow.communicator import Communicator, ApiLimitException, urlopen, JSONError

class TestCommunicator(object):

    @pytest.fixture
    def comm(self):
        comm = Communicator(apiKey="testKey", baseURL="http://data.tpg.ch",
            apiVersion="v99",responseFormat="json")
        return comm

    """ testing composing url"""
    def test_composeUrl_emptyCommand_testsBaseSettings(self, comm):
        generatedUrl = comm.composeUrl("myCommand")
        assert "key=testKey" in generatedUrl
        assert "v99" in generatedUrl
        assert "json" in generatedUrl
        assert "http://data.tpg.ch" in generatedUrl

    def test_composeUrl_withArguments(self, comm):
        generatedUrl = comm.composeUrl("myCommand", stopCode="abcdef", linesCode="9999")
        assert "linesCode=9999" in generatedUrl
        assert "stopCode=abcdef" in generatedUrl

    def test_composeUrl_keyChange(self, comm):
        comm.apiKey = "modifiedKey"
        assert "key=modifiedKey" in comm.composeUrl("myCommand")

    def test_composeUrl_urlChange(self, comm):
        comm.baseURL = "http://alternative.ch"
        generatedUrl = comm.composeUrl("myCommand")
        assert "http://alternative.ch" in generatedUrl

    """ testing JSON decoding errors """
    def test_sendRequest_getJSON_throwsParseException(self):
        mock = Communicator()
        mock.sendRequest = MagicMock(return_value="""{ dcac:}""")
        with pytest.raises(JSONError):
            mock.sendRequest_getJSON("command")

    def test_sendRequest_getJSON_athrowsParseException(self):
        mock = Communicator()
        mock.sendRequest = MagicMock(return_value="""{"abc": 12}""")
        assert mock.sendRequest_getJSON("command") == json.loads("""{"abc": 12}""")

    """ Maximum Requests tests """
    @patch("tpgnow.communicator.urlopen")
    def test_maxRequests_requestsAvailable(self, mock_urlopen):
        mockRead = MagicMock()
        mockRead.read.return_value = "ServerResponse"
        mock_urlopen.return_value = mockRead

        comm = Communicator(maxRequestsPerDay=20)
        assert comm.sendRequest_withCounter("someUrl") == "ServerResponse"
        mock_urlopen.assert_called_once()

    @patch("tpgnow.communicator.urlopen")
    def test_maxRequests_maximumIsZero(self, mock_urlopen):
        mockRead = MagicMock()
        mockRead.read.return_value = "ServerResponse"
        mock_urlopen.return_value = mockRead
        comm = Communicator(maxRequestsPerDay=0)
        with pytest.raises(ApiLimitException):
            comm.sendRequest_withCounter("someUrl")
        mock_urlopen.assert_not_called()

    @patch("tpgnow.communicator.urlopen")
    def test_maxRequests_maximumIsOne_twoRequests_shouldThrowException(self, mock_urlopen):
        mockRead = MagicMock()
        mockRead.read.return_value = "ServerResponse"
        mock_urlopen.return_value = mockRead
        comm = Communicator(maxRequestsPerDay=1)
        with pytest.raises(ApiLimitException):
            comm.sendRequest_withCounter("someUrl")
            comm.sendRequest_withCounter("someUrl")
        mock_urlopen.assert_called_once()

    @patch("tpgnow.communicator.urlopen")
    def test_maxRequests_tooManyRequestsYesterday_shouldWorkToday(self, mock_urlopen):
        mockRead = MagicMock()
        mockRead.read.return_value = "ServerResponse"
        mock_urlopen.return_value = mockRead

        comm = Communicator(maxRequestsPerDay=2)
        comm.currentCount = 5
        comm.counterDate = datetime.today() - timedelta(1)
        assert comm.sendRequest_withCounter("someUrl") == "ServerResponse"
        mock_urlopen.assert_called_once()
        assert comm.counterDate == datetime.today().date()
        assert comm.currentCount == 1
