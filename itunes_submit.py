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
APP_URL_PREFIX = "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/ng/app/"
APP_URL_SUFFIX = "/ios/versioninfo"

IAP_BUTTON_XPATH = "//h1/a[contains(.,'Add In-App Purchase')]"
IAP_CHECK_ALL_INPUT_XPATH = "//input[@ng-model='master' and @type='checkbox']"
IAP_CHECK_ALL_BUTTON_XPATH = "//a[@ng-click='masterChange()']"
IAP_DONE_BUTTON_XPATH = "//button[@ng-click='closeIapModal(true)']"

DEMO_ACCOUNT_BUTTON_XPATH = "//div[@checkbox-name='demoAccountRequired']/span/a"
DEMO_ACCOUNT_INPUT_XPATH = "//div[@checkbox-name='demoAccountRequired']/span/input"

BUILD_BUTTON_XPATH = "//a[@ng-click='showBuildPicker()' and @ng-show='shouldShowBuildPickerIcon()']"
BUILDS_RADIOS_XPATH = "//div[@itc-radio='tempPageContent.buildModal.chosenBuild']/span/a"
BUILDS_DONE_BUTTON_XPATH = "//button[@ng-click='closeBuildModal(true)']"

SAVE_BUTTON_XPATH = "//button[@ng-click='saveVersionDetails()']"
SUBMIT_FOR_REVIEW_BUTTON_XPATH = "//button[@ng-click='submitForReviewStart()']"
USE_ENCRYPTION_BUTTON_XPATH = "//div[@itc-radio='submitForReviewAnswers.exportCompliance.usesEncryption.value']/span/a"
CONTENT_BUTTON_XPATH = "//div[@itc-radio='submitForReviewAnswers.contentRights.containsThirdPartyContent.value']/span/a"
USE_ADS_BUTTON_XPATH = "//div[@itc-radio='submitForReviewAnswers.adIdInfo.usesIdfa.value']/span/a"
ENCRYPTION_COMPLIANCE_BUTTON_XPATH = "//div[@itc-radio='submitForReviewAnswers.exportCompliance.encryptionUpdated.value']/span/a"
YES_INDEX = 0
NO_INDEX = 1
SERVE_ADS_BUTTON_XPATH = "//div[contains(.,'Serve advertisements within the app')]/div/span/a"
LIMIT_TRACKING_BUTTON_XPATH = "//div[@itc-checkbox='submitForReviewAnswers.adIdInfo.limitsTracking.value']/span/a"

SUBMIT_APP_BUTTON_XPATH = "//button[@ng-click='finalizeSubmitForReview()']"
WAITING_FOR_REVIEW_XPATH =  "//a[contains(.,'Waiting For Review')]"

PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/itunes.password"


# Parse inputs
parser = argparse.ArgumentParser(description='Create app on GCM and upload p12 file')
parser.add_argument('-id', required=True, help='App ID')
parser.add_argument('-account', default="", required=False, dest='account', help='Account to use')
parser.add_argument('-user', default="", required=False, dest='user', help='Username to use')
parser.add_argument('-password', default="", required=False, dest='password', help='Password to use')
parser.add_argument('-update', default=False, required=False, dest='updateOnly', action='store_true', help='Update only')
parser.add_argument('-chrome', default=False, required=False, dest='chrome', action='store_true', help='Use chrome web browser')
parser.add_argument('-oldFirefox', default=False, required=False, dest='oldFirefox', action='store_true', help='Use old Firefox web browser')

args = parser.parse_args()
appID = args.id
account = args.account
user = args.user
password = args.password
chrome = args.chrome
oldFirefox = args.oldFirefox
updateOnly = args.updateOnly

if ((account=="") and ((user == "") and (password == ""))):
    print "User -account or -user & -password, but only one of them, and not both!"
    sys.exit()

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            user, password = line.replace("\n","").split(" ")
            accounts[user] = [user, password]
    return accounts

def main():
    print "Submit iOS game on iTunes Connect - by Liran Cohen V1.2"

    # Get credentials
    if account != "":
        user, password = getCredentials(PASSWORDS_FILE)[account]

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
            WebDriverWait(b, 55).until(EC.presence_of_element_located((By.ID, AUTHORIZATION_FRAME_ELEMENT)))
            f = b.find_element(By.ID, AUTHORIZATION_FRAME_ELEMENT)
            b.switch_to_frame(f)
            WebDriverWait(b, 55).until(EC.presence_of_element_located((By.ID, APPLEID_ELEMENT)))
            break
        except selenium.common.exceptions.TimeoutException:
            print "Timed out... retrying..."

    appleID = b.find_element(By.ID, APPLEID_ELEMENT)
    appleID.send_keys(user)
    pwEdit = b.find_element(By.ID, PASSWORD_ELEMENT)
    pwEdit.send_keys(password)
    pwEdit.send_keys(Keys.RETURN)

    # Go to Apps
    WebDriverWait(b, 55).until(EC.presence_of_element_located((By.XPATH, MY_APPS_XPATH)))
    print "Going to app page..."
    b.get(APP_URL_PREFIX + appID + APP_URL_SUFFIX)

    # Check if IAP were added if new version
    if not updateOnly:
        WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, IAP_BUTTON_XPATH)))
        print "Checking & marking IAP..."
        iapButton = b.find_element(By.XPATH, IAP_BUTTON_XPATH)
        iapButton.click()
        WebDriverWait(b,  55).until(EC.presence_of_element_located((By.XPATH, IAP_CHECK_ALL_INPUT_XPATH)))
        iapInput = b.find_element(By.XPATH, IAP_CHECK_ALL_INPUT_XPATH)
        if not iapInput.is_selected():
            # Need to check all
            WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, IAP_CHECK_ALL_BUTTON_XPATH)))
            iapButton = b.find_element(By.XPATH, IAP_CHECK_ALL_BUTTON_XPATH)
            iapButton.click()
        # click DONE
        iapDone = b.find_element(By.XPATH, IAP_DONE_BUTTON_XPATH)
        iapDone.click()

    # Make sure demo account is deactivated
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, DEMO_ACCOUNT_BUTTON_XPATH)))
    print "Verifying demo account is disabled..."
    demoInput = b.find_element(By.XPATH, DEMO_ACCOUNT_INPUT_XPATH)
    if demoInput.is_selected():
        demoButton = b.find_element(By.XPATH, DEMO_ACCOUNT_BUTTON_XPATH)
        demoButton.click()

    # Select first build
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, BUILD_BUTTON_XPATH)))
    print "Selecting first build (this step might fail if build is not yet finished processing, please be aware)..."
    buildButton = b.find_element(By.XPATH, BUILD_BUTTON_XPATH)
    buildButton.click()
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, BUILDS_RADIOS_XPATH)))
    time.sleep(5)
    firstBuild = b.find_elements(By.XPATH, BUILDS_RADIOS_XPATH)[0]
    firstBuild.click()
    buildDone = b.find_element(By.XPATH, BUILDS_DONE_BUTTON_XPATH)
    buildDone.click()

    # Save
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, SAVE_BUTTON_XPATH)))
    print "Saving..."
    saveButton = b.find_element(By.XPATH, SAVE_BUTTON_XPATH)
    saveButton.click()

    # Submit for review
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, SUBMIT_FOR_REVIEW_BUTTON_XPATH)))
    print "Moving to submit form..."
    submitButton = b.find_element(By.XPATH, SUBMIT_FOR_REVIEW_BUTTON_XPATH)
    submitButton.click()

    # Click No, No, Yes
    print "Checking radios..."
    if not updateOnly:
        WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, USE_ENCRYPTION_BUTTON_XPATH)))
        noButton = b.find_elements(By.XPATH, USE_ENCRYPTION_BUTTON_XPATH)[NO_INDEX]
        noButton.click()
        noButton = b.find_elements(By.XPATH, CONTENT_BUTTON_XPATH)[NO_INDEX]
        noButton.click()
    else:
        WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, ENCRYPTION_COMPLIANCE_BUTTON_XPATH)))
        noButton = b.find_elements(By.XPATH, ENCRYPTION_COMPLIANCE_BUTTON_XPATH)[NO_INDEX]
        noButton.click()
    yesButton = b.find_elements(By.XPATH, USE_ADS_BUTTON_XPATH)[YES_INDEX]
    yesButton.click()
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, SERVE_ADS_BUTTON_XPATH)))
    serveAdsButton = b.find_element(By.XPATH, SERVE_ADS_BUTTON_XPATH)
    serveAdsButton.click()
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, LIMIT_TRACKING_BUTTON_XPATH)))
    limitTracking = b.find_element(By.XPATH, LIMIT_TRACKING_BUTTON_XPATH)
    limitTracking.click()

    # Submit
    WebDriverWait(b,  55).until(EC.element_to_be_clickable((By.XPATH, USE_ENCRYPTION_BUTTON_XPATH)))
    print "Submitting for review..."
    submit = b.find_element(By.XPATH, SUBMIT_APP_BUTTON_XPATH)
    submit.click()

    # wait for "Waiting for review..."
    WebDriverWait(b,  55).until(EC.presence_of_element_located((By.XPATH, WAITING_FOR_REVIEW_XPATH)))

    print "Done!"
    b.close()

if __name__ == '__main__':
    main()