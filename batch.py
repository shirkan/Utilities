#!/usr/local/bin/python -u
import sys, time, argparse, json, os, traceback
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# GCM details
LOGIN_URL = 'https://batch.com/login'
LOGIN_USER_ELEMENT = 'username'
LOGIN_PASSWORD_ELEMENT = 'password'

ADD_APP_CLASS = "appnav__new"
APP_NAME_ELEMENT = "app_name"
IOS_PLATFORM_XPATH = "//button[@ng-change='vm.updateSdksList()' and contains(.,'ios')]"
IOS_SDK_XPATH = "//button[@ng-model='vm.app.sdk' and contains(.,'iOS')]"
ADD_APP_XPATH = "//input[@value='Add this app']"

INTEGRATE_BUTTON_XPATH = "//a[@title='Integrate Batch SDK']/span"
API_KEY_XPATH = "//span[contains(.,'// live')]"
P12_FILE_DROPZONE_CSS = 'input[ngf-select]'
JS_INPUT_FILE = "$('input[type=\"file\"')[0]"
JS_INPUT_FILE_STYLE = JS_INPUT_FILE + ".style"

USE_THIS_CERTIFICATE_XPATH = "//button[contains(.,'Use this certificate')]"

PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/batch.password"
OLD_FIREFOX_PATH = "/Applications/Old Firefox/Firefox.app/Contents/MacOS/firefox"

# Parse inputs
parser = argparse.ArgumentParser(description='Create app on GCM and upload p12 file')
parser.add_argument('-name', required=True, help='App name')
parser.add_argument('-p12', default="", required=True, help='P12 file to upload')
parser.add_argument('-chrome', default=False, required=False, dest='chrome', action='store_true', help='Use chrome web browser')
parser.add_argument('-oldFirefox', default=False, required=False, dest='oldFirefox', action='store_true', help='Use old Firefox web browser')

args = parser.parse_args()
name = args.name
p12File = args.p12
chrome = args.chrome
oldFirefox = args.oldFirefox

if not os.path.isfile(p12File):
    print "No such file " + p12File + " - quitting."
    sys.exit()

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            return line.split()

def main():
    print "Create game on Batch and upload p12 file - by Liran Cohen V1.1"

    # Get credentials
    user, password = getCredentials(PASSWORDS_FILE)

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

    # Login
    print "Logging in..."
    b.get(LOGIN_URL)
    loginUser = b.find_element(By.ID, LOGIN_USER_ELEMENT)
    loginUser.send_keys(user)
    loginPass = b.find_element(By.ID, LOGIN_PASSWORD_ELEMENT)
    loginPass.send_keys(password)
    loginPass.send_keys(Keys.RETURN)

    # Click on new app
    WebDriverWait(b, 25).until(EC.element_to_be_clickable((By.CLASS_NAME, ADD_APP_CLASS)))
    print "Clicking on new app..."
    time.sleep(5)
    newApp = b.find_element(By.CLASS_NAME, ADD_APP_CLASS)
    newApp.click()

    # Enter App name & select iOS
    WebDriverWait(b, 25).until(EC.element_to_be_clickable((By.ID, APP_NAME_ELEMENT)))
    print "Entering app name..."
    appNameEntry = b.find_element(By.ID, APP_NAME_ELEMENT)
    appNameEntry.send_keys(name)
    iosButton = b.find_element(By.XPATH, IOS_PLATFORM_XPATH)
    iosButton.click()
    time.sleep(2)
    WebDriverWait(b, 25).until(EC.element_to_be_clickable((By.XPATH, IOS_SDK_XPATH)))
    iosButton = b.find_element(By.XPATH, IOS_SDK_XPATH)
    iosButton.click()
    time.sleep(2)
    WebDriverWait(b, 25).until(EC.element_to_be_clickable((By.XPATH, ADD_APP_XPATH)))
    addAppButton = b.find_element(By.XPATH, ADD_APP_XPATH)
    addAppButton.click()

    # Click Integrate button
    time.sleep(3)
    WebDriverWait(b, 25).until(EC.element_to_be_clickable((By.XPATH, INTEGRATE_BUTTON_XPATH)))
    print "Clicking on 'Integrate' button..."
    integrateButton = b.find_element(By.XPATH, INTEGRATE_BUTTON_XPATH)
    integrateButton.click()

    # Get Live API key
    WebDriverWait(b, 25).until(EC.presence_of_element_located((By.XPATH, API_KEY_XPATH)))
    print "Grabbing API Key..."
    apiKey = str(b.find_element(By.XPATH, API_KEY_XPATH).text.split("\"",3)[1])
    print "API Key: " + apiKey

    # Make file upload visible & upload p12 file
    WebDriverWait(b, 25).until(EC.presence_of_element_located((By.CSS_SELECTOR, P12_FILE_DROPZONE_CSS)))
    print "Uploading P12 file..."
    b.execute_script(JS_INPUT_FILE_STYLE + ".visibility = 'visible'; " + JS_INPUT_FILE_STYLE + ".top=0; " + JS_INPUT_FILE_STYLE + ".opacity=1; " + JS_INPUT_FILE_STYLE + ".height='1px'; " + JS_INPUT_FILE_STYLE + ".width='1px'")
    p12Entry = b.find_element(By.CSS_SELECTOR, P12_FILE_DROPZONE_CSS)
    p12Entry.send_keys(p12File)

    # Click on "Use this certificate"
    WebDriverWait(b, 25).until(EC.element_to_be_clickable((By.XPATH, USE_THIS_CERTIFICATE_XPATH)))
    print "Clicking use this certificate..."
    certButton = b.find_element(By.XPATH, USE_THIS_CERTIFICATE_XPATH)
    certButton.click()

    print "Done."
    print "acc respond:" + apiKey
    b.close()

    return
if __name__ == '__main__':
    main()