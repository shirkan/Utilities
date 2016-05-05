#!/usr/local/bin/python -u
import requests, mechanize, cookielib, sys, os
from lxml import html

# Smoothreview details
LOGIN_URL = "https://microworkers.com/login.php"
SITE_URL = "https://microworkers.com/employer.php"
LOGIN_USER_ELEMENT = "Email"
LOGIN_PASSWORD_ELEMENT = "Password"
LOGOUT_URL = "https://microworkers.com/logout.php"
PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/microworkers.passwords"

MAIN_TABLE = 'employeeinfo'
ENTRIES = 'employeelist'
STATUS_LIVE = 'status03.png'
STATUS_ALMOST_COMPLETED = 'status02.png'
STATUS_COLUMN = 'employeeheadercol05'
CAMPAIGN_NAME = 'employeeheadercol01'
COST = 'employeeheadercol02'
PROGRESS = 'employeeheadercol06'
NOT_RATED = 'employeeheadercol07'

MONEY_LEFT_TAG = "clo01"

def dot():
    sys.stdout.write(".")
    sys.stdout.flush()

def getCredentials(inputFile):
        with open(inputFile) as inFile:
            for line in inFile:
                user, password = line.split()
        return (user, password)

def main():
    print "Microworkers info script - by Liran Cohen V1.2"

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
    browser.addheaders = [ ( 'User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' ) ]

    # Login
    res = browser.open(LOGIN_URL, timeout=1.0)
    browser.select_form(nr = 0)
    browser.form[LOGIN_USER_ELEMENT] = user
    browser.form[LOGIN_PASSWORD_ELEMENT] = password
    browser.submit()

    # Go to employer panel
    res = browser.open(SITE_URL, timeout=1.0)
    tree = html.fromstring(res.get_data())
    table = tree.find_class(MAIN_TABLE)
    campaigns = 0
    toReview = 0
    money = 0

    # get campaigns details
    for entry in table[0].find_class(ENTRIES):
        if (STATUS_LIVE in html.tostring(entry.find_class(STATUS_COLUMN)[0])) or (STATUS_ALMOST_COMPLETED in html.tostring(entry.find_class(STATUS_COLUMN)[0])):
            name = html.tostring(entry.find_class(CAMPAIGN_NAME)[0]).split("Year=\">",1)[1].split(":",1)[0]
            cost = html.tostring(entry.find_class(COST)[0]).split("<p>",1)[1].split("</p>",1)[0]
            progress = html.tostring(entry.find_class(PROGRESS)[0]).split("<p>",1)[1].split("</p>",1)[0].replace("<sup>","").replace("</sup>","")
            not_rated = html.tostring(entry.find_class(NOT_RATED)[0]).split("Year=\">",1)[1].split("</a>",1)[0]
            print name.ljust(40), cost.rjust(5), progress.rjust(5), not_rated.rjust(3)
            if not_rated.isdigit():
                toReview += int(not_rated)
            campaigns+=1

    # get money
    moneyTag = tree.find_class(MONEY_LEFT_TAG)[0]
    money = html.tostring(moneyTag).split("<strong>")[2].split("</strong>")[0]

    #Logout
    browser.open(LOGOUT_URL, timeout=1.0)

    print "Total campaigns: " + str(campaigns) + ", Total to review: " + str(toReview)
    print "Money left: " + money + "\n"
    print "Done!"

if __name__ == '__main__':
    main()