#!/usr/local/bin/python -u
from __future__ import print_function
import requests, mechanize, cookielib, sys, os, argparse
from lxml import html
from time import sleep

# Smoothreview details
SMOOTHREVIEW_LOGIN_URL = "http://smoothreviews.com/?manage"
SMOOTHREVIEW_SITE_URL = "http://smoothreviews.com/?history"
SMOOTHREVIEW_LOGOUT_URL = "http://smoothreviews.com/?logout"
SMOOTHREVIEW_LOGIN_USER_ELEMENT = "email"
SMOOTHREVIEW_LOGIN_PASSWORD_ELEMENT = "password"
SMOOTHREVIEW_PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/smoothreviews.passwords"

# Install4Install details
INSTALL4INSTALL_LOGIN_URL = "http://install4install.com/index.php"
INSTALL4INSTALL_SITE_URL = "http://install4install.com/userpanel.php"
INSTALL4INSTALL_LOGOUT_URL = "http://install4install.com/logout.php"
INSTALL4INSTALL_LOGIN_USER_ELEMENT = "username"
INSTALL4INSTALL_LOGIN_PASSWORD_ELEMENT = "password"
INSTALL4INSTALL_PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/install4install.passwords"


parser = argparse.ArgumentParser(description='Create app on GCM and upload p12 file')
parser.add_argument('-i4i', required=False, dest='i4i', action='store_true', help='Include Install4Install')
args = parser.parse_args()
i4i = args.i4i

def dot():
    sys.stdout.write(".")
    sys.stdout.flush()

def getCredentials(inputFile):
        dict = {}
        with open(inputFile) as inFile:
               reviewer = ""
               credDict = {}
               for line in inFile:
                     # Check for reviewer begin
                     if line.startswith('['):

             # If we started a new reviewer (or come up with "end"), store the previous one
                          if not (reviewer == ''):
                              dict[reviewer] = credDict

                          reviewer = line.replace('[','').replace(']','').replace('\n','')
                          credDict = {}
                     else:
                # If not a new reviewer, store credentials
                          user, password = line.split()
                          credDict[user] = password
        dict[reviewer] = credDict
        return dict

def main():
    print("Reviews control script for Smoothreviews & Install4Install - by Liran Cohen V1.2")
    session_requests = requests.session()

    # SMOOTHREVIEWS
    reviewingData = getCredentials(SMOOTHREVIEW_PASSWORDS_FILE)
    # reviewingData = []
    print("Smoothreviews:\n--------------")

    for reviewer in reviewingData:
        print(reviewer + ":")

        for cred in reviewingData[reviewer]:

            # Create payload
            payload = {
               SMOOTHREVIEW_LOGIN_USER_ELEMENT: cred,
               SMOOTHREVIEW_LOGIN_PASSWORD_ELEMENT: reviewingData[reviewer][cred],
            }

            # Perform login
            result = session_requests.post(SMOOTHREVIEW_LOGIN_URL, data = payload, headers = dict(referer = SMOOTHREVIEW_LOGIN_URL))
            if not result.ok:
                print("ERROR! Couldn't login to Smoothreviews for account: " + cred)
            tree = html.fromstring(result.content)
            class_add_app_lbl = tree.find_class('add_app_lbl')
            slots = class_add_app_lbl[0].text_content().replace("\n", "").rstrip().lstrip().split(".")[0]

            # Scrape url
            result = session_requests.get(SMOOTHREVIEW_SITE_URL, headers = dict(referer = SMOOTHREVIEW_SITE_URL))
            if not result.ok:
                print("ERROR! Couldn't scrape Smoothreviews account: " + cred)
            tree = html.fromstring(result.content)

            class_free = tree.find_class('free')

            class_text1 = class_free[0].find_class('text1')
            print(cred + ": " + class_text1[0].text_content().replace("\n", "") + " (" + slots + ")")

            # Logout
            result = session_requests.get(SMOOTHREVIEW_LOGOUT_URL, headers = dict(referer = SMOOTHREVIEW_LOGOUT_URL))

    if i4i:
        # Install4Install
        reviewingData = getCredentials(INSTALL4INSTALL_PASSWORDS_FILE)
        print("Install4Install:\n----------------")
        browser = mechanize.Browser()
        # Enable cookie support for urllib2
        cookiejar = cookielib.LWPCookieJar()
        browser.set_cookiejar( cookiejar )
        browser.set_handle_refresh(False)
        browser.set_handle_equiv( True )
        browser.set_handle_gzip( True )
        browser.set_handle_redirect( True )
        browser.set_handle_referer( True )
        browser.set_handle_robots( False )
        browser.addheaders = [ ( 'User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' ) ]

        for reviewer in reviewingData:
            print(reviewer + ":")

            for cred in reviewingData[reviewer]:
                print(cred, end='')
                while True:
                    try:

                        # Login
                        dot()
                        res = browser.open(INSTALL4INSTALL_LOGIN_URL, timeout=1.0)
                        browser.select_form(nr = 0)
                        browser.form[INSTALL4INSTALL_LOGIN_USER_ELEMENT] = cred
                        browser.form[INSTALL4INSTALL_LOGIN_PASSWORD_ELEMENT] = reviewingData[reviewer][cred]
                        dot()
                        browser.submit()

                        # Go to user panel
                        dot()
                        res = browser.open(INSTALL4INSTALL_SITE_URL, timeout=1.0)

                        # Scrape
                        currPoints = res.get_data().split("mypoints\'>",1)[1].split("|",1)[0]
                        reviewsToDoThisMonth = res.get_data().split("month!\'>",1)[1].split(" remaining",1)[0]

                        # Print
                        print(" " + currPoints + "points, need to do " + reviewsToDoThisMonth + " more reviews this month")

                        #Logout
                        browser.open(INSTALL4INSTALL_LOGOUT_URL, timeout=1.0)

                    except Exception as e:
                        print("Caught exception for account " + cred + " - retrying... " + str(e))
                        browser.open(INSTALL4INSTALL_LOGOUT_URL, timeout=1.0)
                        continue
                    break

    print("Done.")

if __name__ == '__main__':
    main()