#!/usr/local/bin/python -u
from __future__ import print_function
import requests, mechanize, cookielib, sys, os, argparse
from lxml import html
from time import sleep

# Smoothreview details
SMOOTHREVIEW_LOGIN_URL = "http://smoothreviews.com/?manage"
SMOOTHREVIEW_SITE_URL = "http://smoothreviews.com/?settings"
SMOOTHREVIEW_LOGOUT_URL = "http://smoothreviews.com/?logout"
SMOOTHREVIEW_LOGIN_USER_ELEMENT = "email"
SMOOTHREVIEW_LOGIN_PASSWORD_ELEMENT = "password"
SMOOTHREVIEW_PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/smoothreviews.passwords"
LOOK_FOR = "?settings&unskip="
REMOVE_LINK = "http://smoothreviews.com/?settings&unskip="

# Parse inputs
parser = argparse.ArgumentParser(description='Remove skips from smoothreviews account')
# account name
parser.add_argument('-account', required=True, help='Account to upload file to')
account = parser.parse_args().account

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
    print("Remove all skips from Smoothreviews - by Liran Cohen V1.0")

    reviewingData = getCredentials(SMOOTHREVIEW_PASSWORDS_FILE)
    accounts = {}
    for reviewer in reviewingData:
        for acc in reviewingData[reviewer]:
            accounts[acc] = reviewingData[reviewer][acc]

    if not account in accounts:
        print("Cannot find " + account + " details...")
        sys.exit()

    # Create payload
    payload = {
       SMOOTHREVIEW_LOGIN_USER_ELEMENT: account,
       SMOOTHREVIEW_LOGIN_PASSWORD_ELEMENT: accounts[account],
    }

    session_requests = requests.session()
    # Perform login
    result = session_requests.post(SMOOTHREVIEW_LOGIN_URL, data = payload, headers = dict(referer = SMOOTHREVIEW_LOGIN_URL))
    if not result.ok:
        print("ERROR! Couldn't login to Smoothreviews for account: " + cred)
    result = session_requests.get(SMOOTHREVIEW_SITE_URL, headers = dict(referer = SMOOTHREVIEW_SITE_URL))
    occurences = result.content.count(LOOK_FOR)
    print("Removing all " + str(occurences) + " skips...")
    while True:

        content = result.content
        # tree = html.fromstring(result.content)

        occurences = content.count(LOOK_FOR)
        if occurences == 0:
            print("No more skips to do!")
            break

        if occurences % 10 == 0:
            print(str(occurences) + " skips left...")

        nextSkip = content.split(LOOK_FOR)[1].split('\">Remove')[0]
        result = session_requests.get(REMOVE_LINK + nextSkip, headers = dict(referer = SMOOTHREVIEW_SITE_URL))

    print("Done.")

if __name__ == '__main__':
    main()