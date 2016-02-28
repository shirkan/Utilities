#!/usr/local/bin/python
from __future__ import print_function
import requests, mechanize, cookielib, sys, os, argparse, re
from lxml import html
from time import sleep

# Smoothreview details
SMOOTHREVIEW_LOGIN_URL = "http://smoothreviews.com/?manage"
SMOOTHREVIEW_SITE_URL = "http://smoothreviews.com/?manage#add_apps"
SMOOTHREVIEW_LOGOUT_URL = "http://smoothreviews.com/?logout"
SMOOTHREVIEW_LOGIN_USER_ELEMENT = "email"
SMOOTHREVIEW_LOGIN_PASSWORD_ELEMENT = "password"
SMOOTHREVIEW_PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/smoothreviews.passwords"
APP_URL_INPUT = "app_url"
RESULT_MESSAGE = "result_holder"

# Parse inputs
parser = argparse.ArgumentParser(description='Remove skips from smoothreviews account')
# account name
parser.add_argument('-account', required=True, help='Account to upload file to')
# link
parser.add_argument('-link', required=True, help='Link of new app')

account = parser.parse_args().account
link = parser.parse_args().link

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
    print("Add new game to Smoothreviews - by Liran Cohen V1.0")

    #login
    reviewingData = getCredentials(SMOOTHREVIEW_PASSWORDS_FILE)
    accounts = {}
    for reviewer in reviewingData:
        for acc in reviewingData[reviewer]:
            accounts[acc] = reviewingData[reviewer][acc]

    if not account in accounts:
        print("Cannot find " + account + " details...\nAavailable accounts:\n" + str(accounts))
        sys.exit()

    # Create payload
    payload = {
       SMOOTHREVIEW_LOGIN_USER_ELEMENT: account,
       SMOOTHREVIEW_LOGIN_PASSWORD_ELEMENT: accounts[account],
    }

    session_requests = requests.session()

    # Perform login
    print("Logging in...")
    result = session_requests.post(SMOOTHREVIEW_LOGIN_URL, data = payload, headers = dict(referer = SMOOTHREVIEW_LOGIN_URL))
    if not result.ok:
        print("ERROR! Couldn't login to Smoothreviews for account: " + cred)

    #add app
    print("Adding app...")
    result = session_requests.get(SMOOTHREVIEW_SITE_URL, headers = dict(referer = SMOOTHREVIEW_SITE_URL))
    payload = {
        APP_URL_INPUT: link
    }

    #submit
    result = session_requests.post(SMOOTHREVIEW_SITE_URL, data = payload, headers = dict(referer = SMOOTHREVIEW_SITE_URL))

    #parse respond
    tree = html.fromstring(result.content)
    dataClass = tree.find_class(RESULT_MESSAGE)
    res = html.tostring(dataClass[0])
    print("Result: " + str(re.sub('<[^>]+>', '', res)))

    print("Done.")

if __name__ == '__main__':
    main()