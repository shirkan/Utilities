#!/usr/local/bin/python -u
import sys, time, argparse, json, os, traceback
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


LOGIN_URL = "https://itunesconnect.apple.com/itc/static/login"
AUTHORIZATION_FRAME_ELEMENT = "authFrame"
APPLEID_ELEMENT = "appleId"
PASSWORD_ELEMENT = "pwd"

MY_APPS_XPATH = "//span[contains(.,'My Apps')]"
APPS_URL = "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/ng/app"

APP_URL_PREFIX = "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/ng/app/"
APP_URL_SUFFIX = "/pricing"

PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/itunes.password"


# Parse inputs
parser = argparse.ArgumentParser(description='Create app on GCM and upload p12 file')
parser.add_argument('-account', default="", required=False, dest='account', help='Account to use')
parser.add_argument('-user', default="", required=False, dest='user', help='Username to use')
parser.add_argument('-password', default="", required=False, dest='password', help='Password to use')
parser.add_argument('-allAccounts', default=False, required=False, dest='allAccounts', action='store_true', help='Iterate all accounts')
parser.add_argument('-addall', default=True, required=False, dest='addall', action='store_true', help='Make available to all countries')
parser.add_argument('-removeCountry', default="", required=False, dest='removeCountry', help='Make unavailable from specific country')
parser.add_argument('-chrome', default=False, required=False, dest='chrome', action='store_true', help='Use chrome web browser')
parser.add_argument('-oldFirefox', default=False, required=False, dest='oldFirefox', action='store_true', help='Use old Firefox web browser')

args = parser.parse_args()
account = args.account
user = args.user
password = args.password
chrome = args.chrome
oldFirefox = args.oldFirefox
allAccounts = args.allAccounts
addall = args.addall
removeCountry = args.removeCountry

options = (0 if account=="" else 1) + (0 if (user == "") and (password == "") else 1) + (0 if not allAccounts else 1)

if options != 1:
    print "Use -account or (-user & -password) or -allAccounts, but only one of them, and not all together!"
    sys.exit()

if removeCountry != "":
    print "Remove country is not yet supported..."
    sys.exit()

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            user, password = line.replace("\n","").split(" ")
            accounts[user] = [user, password]
    return accounts

def main():
    global account
    print "Change availability on iTunes Connect (AKA Panic Script) - by Liran Cohen V1.0"

    # Get credentials
    accounts = getCredentials(PASSWORDS_FILE)
    if account != "":
        temp = accounts[account]
        accounts = {}
        accounts[account] = temp

    for account in accounts:
        user, password = accounts[account]

        print "Handling account " + user

        try:
            if chrome:
                print "Opening chrome..."
                b = webdriver.Chrome('/Users/Shirkan/Github/AppNinjaz/Utilities/chromedriver')
            else:
                if oldFirefox:
                    print "Opening old firefox..."
                    binary = FirefoxBinary(OLD_FIREFOX_PATH)
                    b = webdriver.Firefox(firefox_binary=binary)
                else:
                    print "Opening firefox..."
                    b = webdriver.Firefox()
        except selenium.common.exceptions.WebDriverException:
            print "Failed to connect to firefox, this usually happens after version change..."
            print traceback.format_exc()
            sys.exit()
        b.maximize_window()

        # Login
        print "Logging in..."
        while True:
            try:
                b.get(LOGIN_URL)
                WebDriverWait(b, 25).until(EC.presence_of_element_located((By.ID, AUTHORIZATION_FRAME_ELEMENT)))
                f = b.find_element(By.ID, AUTHORIZATION_FRAME_ELEMENT)
                b.switch_to_frame(f)
                WebDriverWait(b, 25).until(EC.presence_of_element_located((By.ID, APPLEID_ELEMENT)))
                break
            except selenium.common.exceptions.TimeoutException:
                print "Timed out... retrying..."

        appleID = b.find_element(By.ID, APPLEID_ELEMENT)
        appleID.send_keys(user)
        pwEdit = b.find_element(By.ID, PASSWORD_ELEMENT)
        pwEdit.send_keys(password)
        pwEdit.send_keys(Keys.RETURN)

        # Go to Apps
        WebDriverWait(b, 25).until(EC.presence_of_element_located((By.XPATH, MY_APPS_XPATH)))
        print "Going to apps page..."
        b.get(APPS_URL)
        WebDriverWait(b, 25).until(EC.visibility_of_element_located((By.ID, "manage-your-apps-search")))

        while True:
            time.sleep(10)
            print "Collecting apps IDs..."
            allLinks = b.find_elements(By.XPATH,"//a[contains(@href,'ios/versioninfo')]")
            allApps = []
            for link in allLinks:
                link = str(link.get_attribute("href"))
                allApps.append(link.split("app/")[1].split("/ios")[0])
            allApps = list(set(allApps))
            print "Found " + str(len(allApps)) + " apps."
            if len(allApps) > 0:
                break

        count = 1
        for app in allApps:
            print "(" + str(count) + "\\" + str(len(allApps)) + ") - Going to page of app id " + app
            b.get(APP_URL_PREFIX + app + APP_URL_SUFFIX)
            try:
                WebDriverWait(b,  25).until(EC.element_to_be_clickable((By.XPATH, "//a[@on-click-func='editAvailability()' and @text='Edit' and @disable='isAvailabilityEditDisabled()']")))
                editButton = b.find_element(By.XPATH, "//a[@on-click-func='editAvailability()' and @text='Edit' and @disable='isAvailabilityEditDisabled()']")
                editButton.click()
            except selenium.common.exceptions.TimeoutException:
                try:
                    WebDriverWait(b,  25).until(EC.element_to_be_clickable((By.XPATH, "//a[@on-click-func='editAvailability()' and @text='Edit' and @disable='false']")))
                    editButton = b.find_element(By.XPATH, "//a[@on-click-func='editAvailability()' and @text='Edit' and @disable='false']")
                    editButton.click()
                except selenium.common.exceptions.TimeoutException:
                    print "(" + str(count) + "\\" + str(len(allApps)) + ") - Skipping, cannot find edit and change app id " + app
                    count+=1
                    continue

            if addall:
                print "(" + str(count) + "\\" + str(len(allApps)) + ") - Changing to \"Available All\" to app id " + app
                try:
                    WebDriverWait(b,  25).until(EC.element_to_be_clickable((By.XPATH, "//span[@checkboxes='tempPageContent.countrySelectionsFilteredByRegion']/a")))
                except selenium.common.exceptions.TimeoutException:
                    print "(" + str(count) + "\\" + str(len(allApps)) + ") - Skipping, cannot find all checkbox and change app id " + app
                    count+=1
                    continue
                allButton = b.find_element(By.XPATH, "//span[@checkboxes='tempPageContent.countrySelectionsFilteredByRegion']/a")
                allButtonInput = b.find_element(By.XPATH, "//span[@checkboxes='tempPageContent.countrySelectionsFilteredByRegion']/input")
                if not allButtonInput.is_selected():
                    # only if need to click then click and press done
                    allButton.click()
                    doneButton = b.find_element(By.XPATH, "//button[@ng-click='saveAvailabilityInfo()']")
                    doneButton.click()
                    WebDriverWait(b,  25).until(EC.element_to_be_clickable((By.XPATH, "//button[@ng-click='savePricingDetails()']")))
                    print "(" + str(count) + "\\" + str(len(allApps)) + ") - Saving app id " + app
                    saveButton = b.find_element(By.XPATH, "//button[@ng-click='savePricingDetails()']")
                    saveButton.click()
                    WebDriverWait(b,  25).until(EC.visibility_of_element_located((By.XPATH, "//span[@ng-show='tempPageContent.showSaveConfirm']")))
                else:
                    print "(" + str(count) + "\\" + str(len(allApps)) + ") - Skipping, already \"Available All\" for app id " + app


            print "(" + str(count) + "\\" + str(len(allApps)) + ") - Done app id " + app
            count+=1

        print "Done with account " + user
        b.close()
        time.sleep(2)

    print "Done!"

if __name__ == '__main__':
    main()