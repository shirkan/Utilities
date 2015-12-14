#!/usr/local/bin/python
import argparse, mechanize, cookielib, sys
from lxml import html

# consts
PASSWORDS_FILE = "universe.password"
LOGIN_URL = "http://universe.appninjaz.com/login"
LOGIN_USER_ELEMENT = "identity"
LOGIN_PASSWORD_ELEMENT = "password"
NEW_APP_URL = "http://universe.appninjaz.com/applications/create"
APP_NAME = "name"
TEMPLATE = "template"
TEMPLATE_TYPE = {
    'slots v3' : "56318a888c0a5abb348b4567",
    'slots v3 android' : "56318ad78c0a5ae5348b4567",
    'dentist' : "54902dc339e97a91568b4567"
}
APPS_PAGE = "http://universe.appninjaz.com/applications"


APP_PAGE_PREFIX = "http://universe.appninjaz.com/applications/"
APP_PAGE_SUFFIX = "/edit"
FLURRY_DEFAULT_SLOTS = "6ZWFRK3TB3SBSBSNFYGK"
FLURRY_DEFAULT_DENTIST = "5ZNZT4MCTW24Q45JCX3B"

# Parse inputs
parser = argparse.ArgumentParser(description='Create parse app and retrieve info')
# game name
parser.add_argument('-name', required=True, help='Game name')
# template name
parser.add_argument('-template', required=True, choices = ['slots v3', 'slots v3 android', 'dentist'], help='which template to open the game in')
# flurry id
parser.add_argument('-flurry', required=True, help='Flurry ID')

args = parser.parse_args()
template = args.template
name = args.name
flurry = args.flurry

def getCredentials(inputFile):
    with open(inputFile) as inFile:
        for line in inFile:
            user, password = line.split()
    return (user, password)

print "Universe create new app script - by Liran Cohen V1.0"

# Get credentials
user, password = getCredentials(PASSWORDS_FILE)

browser = mechanize.Browser()
# Enable cookie support for urllib2
cookiejar = cookielib.LWPCookieJar()
browser.set_cookiejar( cookiejar )
browser.set_handle_refresh(False)
browser.set_handle_equiv( True )
# browser.set_handle_gzip( True )
browser.set_handle_redirect( True )
browser.set_handle_referer( True )
browser.set_handle_robots( False )
browser.addheaders = [ ( 'User-agent', 'Mozilla/15.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' ) ]

# Login
print "Logging in " + user + "..."
res = browser.open(LOGIN_URL, timeout=15.0)
browser.select_form(nr = 0)
browser.form[LOGIN_USER_ELEMENT] = user
browser.form[LOGIN_PASSWORD_ELEMENT] = password
res = browser.submit()

# create new app
print "Creating new game " + name + " with template of " + template + "..."
res = browser.open(NEW_APP_URL, timeout=15.0)
browser.select_form(nr = 0)
browser.form[APP_NAME] = name
browser.form[TEMPLATE] = [TEMPLATE_TYPE[template],]
res = browser.submit()

# get server ID
print "Parsing ID..."
res = browser.open(APPS_PAGE, timeout=15.0)
tree = html.fromstring(res.get_data())
table = tree.find_class('table')
last_row = html.tostring(table[0].getchildren()[1].getchildren()[-1])
if not name in last_row:
    print "Couldn't find created game with name " + name + " in the last row... that's bizarre :("
    sys.exit()
gameID = last_row.split("delete_",1)[1].split("\"",1)[0]
print "Server ID for game is: " + gameID

# update flurry ID
print "Updating flurry id " + flurry
site = APP_PAGE_PREFIX + gameID + APP_PAGE_SUFFIX
res = browser.open(site, timeout=15.0)
browser.select_form(nr = 0)

valueToLookFor = FLURRY_DEFAULT_DENTIST if template == 'dentist' else FLURRY_DEFAULT_SLOTS
foundFlurry = False
for control in browser.form.controls:
    if control.value == valueToLookFor:
        control.value = flurry
        foundFlurry = True
        res = browser.submit()
        break

if not foundFlurry:
    print "Couldn't found Flurry entry in game :("

print "Done."
