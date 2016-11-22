# flake8: noqa
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


_SHAVAR_DEPL = [['stage', 'https://shavar.stage.mozaws.net/']]
_ABSEARCHDEPLOY = [['stage', 'https://search.stage.mozaws.net'],
                   ['prod', 'https://search.services.mozilla.com']]
_ABDESC = """\
The ABSearch Service is used by Firefox to a/b test new search settings.
"""
_ABBUGZILLA = ["Cloud Services", "Server: absearch"]
_WEBEXTLINKS = [['Test Suite', '',
    'https://testrail.stage.mozaws.net/index.php?/suites/view/37']]

_AMOLINKS = [
   ['Functional', 'Tests for AMO', 'https://github.com/mozilla/Addon-Tests'],
   ['Server UI Tests', 'Tests for server',
   'https://github.com/mozilla/addons-server/tree/master/tests/ui'],
   ['Client UI Tests', 'Tests for client',
   'https://github.com/mozilla/addons-frontend/tree/master/tests/ui']
        ]

_SYNCLINK = [
 ['Documentation', 'This is the starting point.' ,
 'https://wiki.mozilla.org/Services/Sync']
        ]

# name, desc, primary, secondary, irc, group, deployments, bugzilla info, links
PROJS = [
        # Customization projects
        ["PageShot", "Test Pilot", "Peter", "Softvision", "#pageshot",
         "Customization", [], [], []],
        ["NoMore404s", "Test Pilot", "Karl", "Softvision", "#testpilot",
         "Customization", [], [], []],
        ["MinVid", "Test Pilot", "Peter", "Softvision", "#testpilot",
         "Customization", [], [], []],
        ["Fathom", "Test Pilot", "Peter", "Softvision", "#testpilot",
         "Customization", [], [], []],
        ["Heatmap", "Test Pilot", "Peter", "Softvision", "#testpilot",
         "Customization", [], [], []],
        ["Universal Search", "Test Pilot", "Stephen", "Peter",
         "#universal-search", "Customization", [], [], []],
        ["Activity Stream", "Test Pilot", "Peter", "John",
         "#activity-stream", "Customization", [], [], []],
        ["WebExtensions", "", "Krupa", "Softvision",
         "#webextensions", "Customization", [], [], _WEBEXTLINKS],
        ["Test Pilot", "", "Peter", "John",
         "#testpilot", "Customization", [], [], []],
        ["Socorro", "", "Matt", "Stephen",
         "#socorro", "Customization", [], [], []],
        ["Telemetry", "", "John", "Softvision",
         "#telemetry", "Customization", [], [], []],
        ["addons.mozilla.org", "", "Krupa", "Softvision",
         "#amo", "Customization", [], [], _AMOLINKS],
        ["TabCenter", "Test Pilot", "Peter", "Softvision",
         "#testpilot", "Customization", [], [], []],
        ["Blok", "Test Pilot", "Rebecca", "Softvision",
         "#testpilot", "Customization", [], [], []],

        # User Interface projects
        ["Treeherder", "", "Rebecca", "Dave", "#treeherder", "User Interfaces",
         [], [], [
             ['Tests', 'https://github.com/mozilla/treeherder-tests']]],
        ["developer.mozilla.org", "", "Matt", "Dave", "#mdndev",
         "User Interfaces", [], [], [
             ['UI Tests', 'https://github.com/mozilla/kuma/tree/master/tests/ui'],
             ['Functional Tests',
                 'https://github.com/mozilla/kuma/tree/master/tests/functional']]],


        ["mozilla.org", "", "Rebecca", "Dave", "#bedrock", "User Interfaces",
            [], [], [['Functional tests', 'https://github.com/mozilla/bedrock/tree/master/tests/functional']]],
        ["FoxPuppet", "", "Benny", "Dave", "#fx-test",
         "User Interfaces", [], [], []],
        ["Activity Stream (iOS)", "", "Aaron", "No-Jun", "#mobile",
         "User Interfaces", [], [], []],
        ["Activity Stream (Android)", "", "Kevin", "No-Jun", "#mobile",
         "User Interfaces", [], [], []],
        ["Prox (iOS)", "", "Aaron", "No-Jun", "#mobile",
         "User Interfaces", [], [], []],
        ["Focus (iOS)", "", "Aaron", "No-Jun", "#mobile",
         "User Interfaces", [], [], []],

        # Services project
        ["ABSearch", _ABDESC, "Karl", "Chris", "#absearch", "Services",
         _ABSEARCHDEPLOY, _ABBUGZILLA, []],
        ["Balrog", "", "Chris", "Karl", "#balrog", "Services", [], [], []],
        ["Bouncer", "", "Matt", "Dave", "#stubby", "Services", [], [], [
            ['End2end test',
            'https://github.com/mozilla-services/go-bouncer/tree/master/tests/e2e']
            ]],
        ["Firefox Accounts", "", "Karl", "Peter", "#fxa", "Services", [], [], [
            ['Content Server Tests',
                'https://github.com/mozilla/fxa-content-server#testing'],
            ['FxaPom', 'https://github.com/mozilla/fxapom']
            ]],

        ["Kinto", "", "Chris", "Karl", "#storage", "Services", [], [], []],
        ["Loads", "", "Richard", "Chris", "#fx-test", "Services", [], [], []],
        ["Push Notification", "", "Richard", "Rebecca", "#push", "Services", [], [], [
            ['Github', 'https://github.com/mozilla-services/autopush'],
            ['Documentation', 'http://autopush.readthedocs.io/'],
            ['Load test', 'https://github.com/mozilla-services/ap-loadtester']]],
        ["Shavar", "Tracking Protection", "Rebecca", "Richard", "#shavar",
         "Services", _SHAVAR_DEPL, [], [
             ['Load Test', 'https://github.com/rpappalax/shavar-loadtests'],
             ['Code+Test', 'https://github.com/mozilla-services/shavar/'
             ]]],
        ["SHIELD", "", "Chris", "Karl", "#normandy", "Services", [], [], []],
        ["Stub Attribution", "", "Stephen", "Matt", "#stubby", "Services", [],
                [], [["Project Page",
                     'https://wiki.mozilla.org/Firefox/Stub_Attribution'],
                     ['Unit test',
                       'https://github.com/mozilla-services/stub_attribution'],
                     ['Unit test (bedrock)',
                      'https://github.com/mozilla/bedrock/tree/master/bedrock/firefox/tests'
                     ]]],

        ["Sync", "", "Karl", "Chris", "#sync", "Services", [], [], _SYNCLINK]

]
