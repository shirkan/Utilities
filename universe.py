#!/usr/local/bin/python
import argparse, mechanize, cookielib, sys
from lxml import html

# consts
PASSWORDS_FILE = "flurry.password"
LOGIN_URL = "https://dev.flurry.com/secure/login.do"
LOGIN_USER_ELEMENT = "loginEmail"
LOGIN_PASSWORD_ELEMENT = "loginPassword"
IOS_NEW_APP_URL = "https://dev.flurry.com/iphone_createProject.do"
ANDROID_NEW_APP_URL = "https://dev.flurry.com/android_createProject.do"
APP_NAME = "projectName"
CATEGORY_ID = "categoryId"
IOS_SLOT_TYPE = "141"
ANDROID_SLOT_TYPE = "623"
DENTIST_TYPE = "145"
CODE_CLASS = "projectKey"

# Parse inputs
parser = argparse.ArgumentParser(description='Create parse app and retrieve info')
# game name
parser.add_argument('-name', required=True, help='Game name')
# platform name
parser.add_argument('-platform', required=True, choices = ['ios', 'android'], help='which platform to open the game in')
# type
parser.add_argument('-type', required=True, choices = ['slot', 'dentist'], help='which type of game to open')

args = parser.parse_args()
platform = args.platform
name = args.name
type = args.type

def getCredentials(inputFile):
        with open(inputFile) as inFile:
            for line in inFile:
                user, password = line.split()
        return (user, password)

print "Flurry create new app script - by Liran Cohen V1.0"

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
print "Logging in " + user + "..."
res = browser.open(LOGIN_URL, timeout=5.0)
# print "Step 1: \n" + res.get_data()
# print "----------------------------------------------------------------------"
browser.select_form(nr = 0)
browser.form[LOGIN_USER_ELEMENT] = user
browser.form[LOGIN_PASSWORD_ELEMENT] = password
res = browser.submit()
# print "Step 2: \n" + res.get_data()
# print "----------------------------------------------------------------------"

# Go to employer panel
site = IOS_NEW_APP_URL if platform == 'ios' else ANDROID_NEW_APP_URL
category = DENTIST_TYPE if type == 'dentist' else (IOS_SLOT_TYPE if platform == 'ios' else ANDROID_SLOT_TYPE)

print "Creating new " + platform + " " + type + " game named " + name + "..."
res = browser.open(site, timeout=5.0)
# print "Step 3: \n" + res.get_data()
# print "----------------------------------------------------------------------"
browser.select_form(name = "createProjectActionForm")
browser.form[APP_NAME] = name + " - " + platform[:3].upper()
browser.form[CATEGORY_ID] = [category,]
res = browser.submit()
# print "Step 4: \n" + res.get_data()
# print "----------------------------------------------------------------------"

print "Parsing ID..."

tree = html.fromstring(res.get_data())
code = tree.find_class(CODE_CLASS)

print html.tostring(code[0]).split("projectKey\">",1)[1].split("</",1)[0]

print "Done."
