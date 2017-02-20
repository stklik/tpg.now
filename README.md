tpg.now
===
by [@stklik](http://twitter.com/stklik)

**tpg.now** is an app that shows live data for the Geneva Public Transport system ([TPG](http://www.tpg.ch)).  
(the data is provided by TPG itself, the correctness lies in their hands)


Usage:
---
Add filters and choices separated by slashes (`/`)  
e.g. `tpgnow.herokuapp.com/CERN/18` to display departures of the line 18 from CERN

Arguments:
---
| argument | effect |
|---|---|
| `/help` | display this message|
| `/info` | get info about the lines and stops operated today|
| `/info/stops` | same as /info but only displays stop information|
| `/info/lines` | same as /info but only displays line information|
| `/<stop>` | enter ONE stop name or code for which you want the departures <br /> find stop names and codes on localhost:5000/info/stops <br /> e.g. [`tpgnow.herokuapp.com/AERO`](http://tpgnow.herokuapp.com/Cornavin) or [`tpgnow.herokuapp.com/AERO`](http://tpgnow.herokuapp.com/AERO) |
|`/<stop>/<line>`      | optionally add one or more line codes to filter <br /> e.g. [`tpgnow.herokuapp.com/CERN/18/Y`](http://tpgnow.herokuapp.com/CERN/18/Y) to filter lines 18 and Y |
|`/compact`            | switches to compact output format|
|`/times`              | displays the departure times, rather than waiting time|


Hint:
---
try using it from CLI with `curl`
e.g. [`curl tpgnow.herokuapp.com/CERN`](http://tpgnow.herokuapp.com/CERN)

Todo:
---
- [ ] add tests
- [ ] implement handling of Communicator exceptions

---
tpg.now by [@stklik](http://twitter.com/stklik) -
Follow for updates.
