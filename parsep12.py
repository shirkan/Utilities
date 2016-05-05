#!/usr/local/bin/python -u
import requests, mechanize, cookielib, sys, time
import argparse,json,httplib,os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Parse details
LOGIN_URL = "https://www.parse.com/login"
LOGIN_USER_ELEMENT = "user_session[email]"
LOGIN_PASSWORD_ELEMENT = "user_session[password]"
PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/parse.password"

# Parse inputs
parser = argparse.ArgumentParser(description='Create parse app and retrieve info')
# account name
parser.add_argument('-account', required=True, help='Account to upload file to')
# p12 file
parser.add_argument('-file', default="", required=False, help='P12 file to upload')
# app name
parser.add_argument('-app', required=False, help='App to upload p12 to')

args = parser.parse_args()
account = args.account
p12File = args.file
selectedApp = args.app
printOnly = False

if p12File == "" or not os.path.isfile(p12File):
    print "No such file " + p12File + ", printing only"
    printOnly = True

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            name, user, password = line.split()
            accounts[name] = [user, password]
            accounts[user] = [user, password]
    return accounts

def getApps(user, password):
    apps = {}
    print "Getting all apps for account " + user
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/apps', '', {
       "X-Parse-Email": user,
       "X-Parse-Password": password,
       "Content-Type": "application/json"
     })
    result = json.loads(connection.getresponse().read())
    for app in result['results']:
        name = app['appName']
        url = app['dashboardURL'].replace("www","dashboard") + "/settings/push"
        apps[name] = url
    # print apps
    return apps

def printApps(apps):
    for app in apps:
        print app

def selectApp(apps, selectedapp):
    if selectedapp!="":
        return apps[selectedapp]

    appLists = apps.keys();
    while True:
        sys.stdout.flush()
        i = 0;
        for app in appLists:
            print "[" + str(i) + "] " + app
            i+=1
        print "[" + str(i) + "] Exit"
        option = int(input("Select option:\n"))
        if option == i:
            sys.exit()
        if option>=0 and option<=i:
            break
    return apps[appLists[option]]

def main():
    print "Parse upload p12 file - by Liran Cohen V1.0"

    accounts = getCredentials(PASSWORDS_FILE)
    if not account in accounts:
        print "Cannot find credentials for account " + account + "\n"
        print "Available accounts: " + str(accounts.keys())
        sys.exit()

    # Get credentials
    user, password = accounts[account]

    # Get games list
    apps = getApps(user, password)
    sys.stdout.flush()

    if printOnly:
        printApps(apps)
        sys.exit()

    # print menu
    url = selectApp(apps, selectedApp)

    print "Opening browser and uploading p12 file..."

    b = webdriver.Firefox()

    # login
    b.get(LOGIN_URL)
    loginUser = b.find_element_by_name(LOGIN_USER_ELEMENT)
    loginPass = b.find_element_by_name(LOGIN_PASSWORD_ELEMENT)
    loginUser.send_keys(user)
    loginPass.send_keys(password)
    loginPass.send_keys(Keys.RETURN)

    WebDriverWait(b, 25).until(EC.presence_of_element_located((By.ID, "appsData")))

    # go to URL
    b.get(url)
    WebDriverWait(b, 25).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    uploadButton = b.find_element_by_xpath("//input[@type='file']")
    uploadButton.send_keys(p12File)

    print "Uploading p12... sleeping for 10 seconds..."
    time.sleep(10)

    print "Refreshing... please check file was uploaded. Sleeping for 15 seconds..."
    b.refresh();
    time.sleep(15)

    print "Done! closing..."
    b.quit()

    return
if __name__ == '__main__':
    main()