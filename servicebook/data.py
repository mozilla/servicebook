
PEOPLE = """\
Stuart Philp
Krupa Raj
Dave Hunt
Richard Pappalardo
Karl Thiessen
Peter deHaan
Chris Hartjes
Stephen Donner
Kevin Brosnan
Aaron Train
Matt Brandt
Rebecca Billings
John Dorlus
No-Jun Park
Benny Forehand Jr.
"""


GROUPS = [("User Interfaces", "https://wiki.mozilla.org/TestEngineering/UI",
           "Dave Hunt"),
          ("Services", "https://wiki.mozilla.org/TestEngineering/Services",
           "Richard Pappalardo"),
          ("Customization",
           "https://wiki.mozilla.org/TestEngineering/Customization",
           "Krupa Raj")]


_ABSEARCHDEPLOY = [['stage', 'https://search.stage.mozaws.net'],
                   ['prod', 'https://search.services.mozilla.com']]
_ABDESC = """\
The ABSearch Service is used by Firefox to a/b test new search settings.
"""
_ABBUGZILLA = ["Cloud Services", "Server: absearch"]


PROJS = [["Shavar (Tracking Protection)", "", "Rebecca", "Richard", "#shavar",
          "Services", [], []],
         ["ABSearch", _ABDESC, "Karl", "Chris", "#absearch", "Services",
          _ABSEARCHDEPLOY, _ABBUGZILLA],
         ["Balrog", "", "Chris", "Karl", "#balrog", "Services", [], []]]
