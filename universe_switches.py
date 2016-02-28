#!/usr/local/bin/python
import argparse, mechanize, cookielib, sys, os
from lxml import html

# consts
PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/universe.password"
LOGIN_URL = "http://universe.appninjaz.com/login"
LOGIN_USER_ELEMENT = "identity"
LOGIN_PASSWORD_ELEMENT = "password"

# for each template, which fields numbers to change
TEMPLATES = {
    'Slot v2' : [17, 23, 29, 42, 56, 57],
    'Slots V2 Tola' : [16, 22, 28, 41, 55, 56],
    'Slots V2 Android' : [16, 22, 28, 39, 49],
    'Slots V3' : [17, 23, 29, 42, 56, 57],
    'Slots V3 Android' : [16, 22, 28, 39, 49],
    'Slots V3 Scam' : [17, 23, 29, 42, 56, 57]
}
APPS_PAGE = "http://universe.appninjaz.com/applications"
TRIGGERS = {
    'ios' : ["custom_ad_1_enabled", "custom_ad_2_enabled", "custom_ad_3_enabled", "enable_custom_ad_lobby", "is_free_coins_btn_live", "is_live"],
    'android' : ["custom_ad_1_enabled", "custom_ad_2_enabled", "custom_ad_3_enabled", "enable_custom_ad_lobby", "is_live"]
}

APP_PAGE_PREFIX = "http://universe.appninjaz.com/applications/"
APP_PAGE_SUFFIX = "/edit"
ONLINE = "Integrated"

# Parse inputs
parser = argparse.ArgumentParser(description='Create parse app and retrieve info')
# start from app
parser.add_argument('-startFrom', default="", required=False, help='Game name')

args = parser.parse_args()
startFrom = args.startFrom

def getCredentials(inputFile):
    with open(inputFile) as inFile:
        for line in inFile:
            user, password = line.split()
    return (user, password)

print "Universe set all switches - by Liran Cohen V1.0"

# Get credentials
user, password = getCredentials(PASSWORDS_FILE)

browser = mechanize.Browser()
# Enable cookie support for urllib2
cookiejar = cookielib.LWPCookieJar()
browser.set_cookiejar( cookiejar )
browser.set_handle_refresh(False)
browser.set_handle_equiv( True )
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

# Iterate apps
res = browser.open(APPS_PAGE, timeout=15.0)
body = html.fromstring(res.get_data())
table = body.find_class("table")[0]
elems = table.xpath("tbody/*")

#flag - can we start check.
canCheck = (startFrom == "")
print "Iterating apps... "

for elem in elems:
    raw = html.tostring(elem)
    id = raw.split("<td>")[1].split("</td>")[0].replace("\n","").replace("\t","")
    name = raw.split("<td>")[2].split("</td>")[0].replace("\n","").replace("\t","")
    type = raw.split("<td>")[3].split("</td>")[0].replace("\n","").replace("\t","")
    status = raw.split("class=\"label")[1].split(">")[1].split("</s")[0].replace("\n","").replace("\t","")
    editLink = raw.split("href=\"")[2].split("\"></a>")[0].replace("\n","").replace("\t","")

    # can we check this entry?
    if not canCheck:
        if startFrom == id:
            canCheck = True
        else:
            continue

    #if we got here, we can check
    # check if type can be handled
    if not type in TEMPLATES:
        continue

    # edit app
    print "Editing app with id: " + id + " - " + name + " (" + type + ", " + status + ")..."
    res = browser.open(editLink, timeout=15.0)
    browser.select_form(nr = 0)

    value = ('1' if status == ONLINE else '0')
    for num in TEMPLATES[type]:
        # print "before " + str(browser.form.controls[num]) + " - " + str(browser.form.controls[num].value)
        browser.form.controls[num].value = [value]
        # print "after " + str(browser.form.controls[num]) + " - " + str(browser.form.controls[num].value)
    browser.submit()
    print "Done."

print "Done all!"