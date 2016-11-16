
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
Softvision Co.
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


# name, desc, primary, secondary, irc, group, deployments, bugzilla info.
PROJS = [
        # Customization projects
        ["PageShot", "Test Pilot", "Peter", "Softvision", "#pageshot",
         "Customization", [], []],
        ["NoMore404s", "Test Pilot", "Karl", "Softvision", "#testpilot",
         "Customization", [], []],
        ["MinVid", "Test Pilot", "Peter", "Softvision", "#testpilot",
         "Customization", [], []],
        ["Fathom", "Test Pilot", "Peter", "Softvision", "#testpilot",
         "Customization", [], []],
        ["Heatmap", "Test Pilot", "Peter", "Softvision", "#testpilot",
         "Customization", [], []],
        ["Universal Search", "Test Pilot", "Stephen", "Peter",
         "#universal-search", "Customization", [], []],
        ["Activity Stream", "Test Pilot", "Peter", "John",
         "#activity-stream", "Customization", [], []],
        ["WebExtensions", "", "Krupa", "Softvision",
         "#webextensions", "Customization", [], []],
        ["Test Pilot", "", "Peter", "John",
         "#testpilot", "Customization", [], []],
        ["Socorro", "", "Matt", "Stephen",
         "#socorro", "Customization", [], []],
        ["Telemetry", "", "John", "Softvision",
         "#telemetry", "Customization", [], []],
        ["addons.mozilla.org", "", "Krupa", "Softvision",
         "#amo", "Customization", [], []],
        ["TabCenter", "Test Pilot", "Peter", "Softvision",
         "#testpilot", "Customization", [], []],
        ["Blok", "Test Pilot", "Rebecca", "Softvision",
         "#testpilot", "Customization", [], []],

        # User Interface projects
        ["Treeherder", "", "Rebecca", "Dave", "#treeherder", "User Interfaces",
         [], []],
        ["developer.mozilla.org", "", "Matt", "Dave", "#mdndev",
         "User Interfaces", [], []],

        # Services projects
        ["Shavar", "Tracking Protection", "Rebecca", "Richard", "#shavar",
         "Services", [], []],
        ["ABSearch", _ABDESC, "Karl", "Chris", "#absearch", "Services",
         _ABSEARCHDEPLOY, _ABBUGZILLA],
        ["Balrog", "", "Chris", "Karl", "#balrog", "Services", [], []]]
