#!/usr/local/bin/python -u
import sys, time, argparse, json, os, traceback, slack
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

YAD2_URL = "http://my.yad2.co.il/MyYad2/MyOrder/Yad2.php"
LOGIN_USER_ELEMENT = "userName"
LOGIN_PASSWORD_ELEMENT = "password"

WAIT_FOR_XPATH = "//a[@href='Yad2.php']"
ADS_XPATH = "//tr[@onmouseout]"
AD_ATTRIBUTE_TO_SEARCH = "onmouseout"
AD_PREFIX = "TxtID"
AD_FRAME_PREFIX = "ifram_info"
AD_DETAILS_XPATH = "//td[@id='REPLACE_ID']"

def main():
    success = []
    fail = []

    print "Yad 2 jumper by Liran Cohen V1.0"
    print "Logging in..."
    user = "gshirkan@gmail.com"
    password = "shirkan"
    b = webdriver.Firefox()
    b.get(YAD2_URL)

    #Login
    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.ID, LOGIN_USER_ELEMENT)))
    loginEntry = b.find_element(By.ID, LOGIN_USER_ELEMENT)
    loginEntry.send_keys(user)
    pwEdit = b.find_element(By.ID, LOGIN_PASSWORD_ELEMENT)
    pwEdit.send_keys(password)
    pwEdit.send_keys(Keys.RETURN)

    # Click YAD2
    print "Moving to YAD2..."
    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.XPATH, WAIT_FOR_XPATH)))
    b.get(YAD2_URL)

    # Iterate ads
    print "Iterating ads..."
    WebDriverWait(b, 55).until(EC.element_to_be_clickable((By.XPATH, ADS_XPATH)))
    ads = b.find_elements(By.XPATH, ADS_XPATH)
    for ad in ads:
        adID = str(ad.get_attribute(AD_ATTRIBUTE_TO_SEARCH).split("\"")[1].replace(AD_PREFIX,""))
        print "Trying to update ad " + str(adID)
        detailsButton = b.find_element(By.XPATH, AD_DETAILS_XPATH.replace("REPLACE_ID", AD_PREFIX + adID))
        detailsButton.click()
        frame = AD_FRAME_PREFIX + adID
        WebDriverWait(b, 55).until(EC.frame_to_be_available_and_switch_to_it((By.ID, frame)))

        aTags = b.find_elements_by_xpath("//a[@onclick]")
        found = False
        for a in aTags:
            if adID + "&Up" in a.get_attribute('onclick') != -1:
                try:
                    a.click()
                    print "Updated item " + str(adID)
                    success.append(str(adID))
                    found = True
                except selenium.common.exceptions.StaleElementReferenceException:
                    print "Updating item " + str(adID)
                break

        if not found:
            print "Cannot update item " + str(adID)
            fail.append(str(adID))

        b.switch_to_default_content()

    time.sleep(10)
    b.close()
    print "Yad2 report\nSuccess: " + str(success) + "\nFail: " + str(fail)
    slack.SLsendMessageToChannel("#my_alerts", "Yad2 report\nSuccess: " + str(success) + "\nFail: " + str(fail))
    print "Done."

if __name__ == '__main__':
    main()