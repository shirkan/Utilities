#!/usr/local/bin/python -u
import sys, time, argparse, json, os, traceback
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

CAMPAIGNS = {
    'adidasbloom@gmail.com' : {
        'CASINO - Big 4' : '537b26931873da554a40103f',
        'Casino  World - IOS' : '543a6385c26ee42f93d424cc'
    },
    'totemediainc@gmail.com' : {
        'CASINO - Big 4' : '56f2550fa8b63c16e67e2438',
        'Casino  World - IOS': '56f256ae8838095e722d9ff9'
    }
}

LOGIN_URL = "https://dashboard.chartboost.com/login?redirect=%2Fall%2Fcampaigns%2F"
LOGIN_NAME_XPATH = "//input[@name='email']"
LOGIN_PASSWORD_XPATH = "//input[@name='password']"

ADVANCED_TARGETING_TAB_XPATH = "//div[@class='tab-title' and contains(.,'Advanced Targeting')]"
BY_ID_BUTTON_XPATH = "//div[@data-tab='block-app-id']"
IGNORE_APP_IDS_NAME = "ignore_apps_id"
SAVE_BUTTON_XPATH = "//button[@type='submit' and contains(.,'Save')]"

FINAL_LABEL_XPATH = "//div[contains(.,'Your campaign has been saved')]"

PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/chartboost.password"

# Parse inputs
parser = argparse.ArgumentParser(description='Create app on GCM and upload p12 file')
parser.add_argument('-ids', required=True, help='IDs to filter out')
parser.add_argument('-campaign', default="", required=False, dest='campaign', help='Campaign to filter')
parser.add_argument('-user', default="", required=True, dest='user', help='Username to use')
# parser.add_argument('-password', default="", required=False, dest='password', help='Password to use')
parser.add_argument('-chrome', default=False, required=False, dest='chrome', action='store_true', help='Use chrome web browser')
parser.add_argument('-oldFirefox', default=False, required=False, dest='oldFirefox', action='store_true', help='Use old Firefox web browser')

args = parser.parse_args()
ids = args.ids
campaign = args.campaign
user = args.user
chrome = args.chrome
oldFirefox = args.oldFirefox

def getCredentials(inputFile):
    accounts = {}
    foundSubject = False
    with open(inputFile) as inFile:
        for line in inFile:
            line = line.rstrip("\n")
            if line == "":
                continue
            if not foundSubject and "[Credentials]" not in line:
                continue
            else:
                if not foundSubject and line == "[Credentials]":
                    foundSubject = True
                else:
                    if foundSubject and line.startswith("["):
                        break
            if len(line.split()) == 1:
                continue
            accounts[line.split()[0]] = line.split()[1]
    return accounts

def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getNumInput(fromIdx, toIdx):
    while True:
        num = raw_input()
        if representsInt(num):
            num = int(num)
            if num>=fromIdx and num<=toIdx:
                return num

def printMenu(menu, isBack=False):
    print '-------------------------'
    i=0
    for key in menu.keys():
        print '[' + str(i) + '] - ' + key
        i+=1
    if isBack:
        print '[' + str(i) + '] - Back'
    print 'Enter option:'
    return getNumInput(0,i)

def main():
    global campaign
    print "Chartboost filter script - by Liran Cohen V1.0"

    # Get credentials
    accounts = getCredentials(PASSWORDS_FILE)
    password = accounts[user]

    if campaign == "" or (campaign not in CAMPAIGNS[user].keys() and campaign not in CAMPAIGNS[user].values()):
        print "Please select campaign to filter:"
        campaign = CAMPAIGNS[user][CAMPAIGNS[user].keys()[printMenu(CAMPAIGNS[user])]]

    if campaign in CAMPAIGNS[user].keys():
        campaign = CAMPAIGNS[user][campaign]

    print "Filtering ids for " + user + " campaign code " + str(campaign)

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
    b.get(LOGIN_URL + campaign)
    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.XPATH, LOGIN_NAME_XPATH)))
    loginEntry = b.find_element(By.XPATH, LOGIN_NAME_XPATH)
    loginEntry.send_keys(user)
    pwEdit = b.find_element(By.XPATH, LOGIN_PASSWORD_XPATH)
    pwEdit.send_keys(password)
    pwEdit.send_keys(Keys.RETURN)

    # Go to advanced targeting
    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.XPATH, ADVANCED_TARGETING_TAB_XPATH)))
    print "Going to advanced targeting page..."
    targetingTab = b.find_element(By.XPATH, ADVANCED_TARGETING_TAB_XPATH)
    targetingTab.click()

    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.XPATH, BY_ID_BUTTON_XPATH)))
    byID = b.find_element(By.XPATH, BY_ID_BUTTON_XPATH)
    byID.click()

    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.NAME, IGNORE_APP_IDS_NAME)))
    print "Entering IDs & submitting..."
    ignoreEdit = b.find_element(By.NAME, IGNORE_APP_IDS_NAME)
    ignoreEdit.send_keys(ids)
    ignoreEdit.send_keys(Keys.RETURN)
    time.sleep(5)
    saveButton = b.find_element(By.XPATH, SAVE_BUTTON_XPATH)
    saveButton.click()

    WebDriverWait(b, 55).until(EC.presence_of_element_located((By.XPATH, FINAL_LABEL_XPATH)))
    print "Successfully saved."
    b.close()
    print "Done!"

if __name__ == '__main__':
    main()