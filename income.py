#!/usr/local/bin/python
import requests, mechanize, cookielib, sys
from lxml import html
from datetime import date, timedelta
import pycurl, json
from StringIO import StringIO

# Buffalo details
BUFFALO_LOGIN_URL = "https://www.buffalopartners.com/"
BUFFALO_LOGIN_USER_ELEMENT = "UserName"
BUFFALO_LOGIN_PASSWORD_ELEMENT = "Password"
BUFFALO_LOGOUT_URL = "https://www.buffalopartners.com/login/logoff"

APPANNIE_LOGIN_URL = "https://www.appannie.com/account/login"
APPANNIE_DATA_PAGE = "https://www.appannie.com/ad_dashboard"
APPANNIE_DAILY_DATA_PAGE = "https://www.appannie.com/ad_dashboard/ad_revenue/#date_range_picker="
APPANNIE_LOGIN_USER_ELEMENT = "username"
APPANNIE_LOGIN_PASSWORD_ELEMENT = "password"

PASSWORDS_FILE = "income.password"
KEYS = ["Buffalo_Main_Account", "Buffalo_Second_Account", "Appannie"]

BUFFALO_EARNINGS_CLASS = "loggedin-highlight"
APPANNIE_API_KEY = "06faf19a08a1eff5da1fd46e50238f5c901e050a"
APPANNIE_SALES = 'sales_list'
APPANNIE_AD_ACCOUNTS = {265056: "Applovin main", 285034: "Chartboost main", 265057: "Playhaven casino", 275073: "Playhaven beezbee", 265060: "Admob", 291338: "Vungle"}

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            name, user, password = line.split()
            accounts[name] = [user, password]
    return accounts

def main():
    print "Income info script - by Liran Cohen V1.0"

    #Buffalo main account
    # Get credentials
    accounts = getCredentials(PASSWORDS_FILE)
    user, password = accounts[KEYS[0]]

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

    # Login Buffalo main account
    print "Login to buffalo with account " + user + "..."
    res = browser.open(BUFFALO_LOGIN_URL, timeout=1.0)
    browser.select_form(nr = 1)
    browser.form[BUFFALO_LOGIN_USER_ELEMENT] = user
    browser.form[BUFFALO_LOGIN_PASSWORD_ELEMENT] = password
    browser.submit()
    res = browser.open(BUFFALO_LOGIN_URL, timeout=1.0)
    tree = html.fromstring(res.get_data())
    table = tree.find_class(BUFFALO_EARNINGS_CLASS)
    earnings = html.tostring(table[0])
    print KEYS[0].replace("_", " ") + ": " + earnings.split(">")[1].split("<")[0]

    # Login Buffalo secondary account
    user, password = accounts[KEYS[1]]
    print "Login to buffalo with account " + user + "..."
    res = browser.open(BUFFALO_LOGOUT_URL, timeout=1.0)
    res = browser.open(BUFFALO_LOGIN_URL, timeout=1.0)
    browser.select_form(nr = 1)
    browser.form[BUFFALO_LOGIN_USER_ELEMENT] = user
    browser.form[BUFFALO_LOGIN_PASSWORD_ELEMENT] = password
    browser.submit()
    res = browser.open(BUFFALO_LOGIN_URL, timeout=1.0)
    tree = html.fromstring(res.get_data())
    table = tree.find_class(BUFFALO_EARNINGS_CLASS)
    earnings = html.tostring(table[0])
    print KEYS[1].replace("_", " ") + ": " + earnings.split(">")[1].split("<")[0]
    res = browser.open(BUFFALO_LOGOUT_URL, timeout=1.0)
    browser.close()

    #Login Appannie
    print "Getting Appannie yesterday's data..."
    yesterday = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    deductFor30 = 30
    b = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.WRITEDATA, b)
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account")
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + yesterday + "&end_date=" + yesterday)
    curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer ' + APPANNIE_API_KEY])
    curl.perform()
    j = json.loads(b.getvalue())

    if (len(j[APPANNIE_SALES]) == 0):
        print "No Appannie info for yesterday, retrieving day before..."
        b.truncate(0)
        yesterday = (date.today() - timedelta(2)).strftime('%Y-%m-%d')
        deductFor30 = 31
        curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + yesterday + "&end_date=" + yesterday)
        curl.perform()
        j = json.loads(b.getvalue())

    print "Appannie info for " + yesterday + ":"
    total = 0
    for i in j[APPANNIE_SALES]:
        if not 'revenue' in i['metric']:
            continue
        total += float(i['metric']['revenue'])
        print APPANNIE_AD_ACCOUNTS[i['ad_account']] + ": " + str(i['metric']['revenue'])

    print "\nTotal: " + str(total)

    thirtyDays = (date.today() - timedelta(deductFor30)).strftime('%Y-%m-%d')
    today = date.today().strftime('%Y-%m-%d')
    print "Getting Appannie last 30 days data (" + thirtyDays + " - " + yesterday + ")..."
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + thirtyDays + "&end_date=" + today)
    curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer ' + APPANNIE_API_KEY])
    b.truncate(0)
    curl.perform()
    j = json.loads(b.getvalue())

    total = 0
    for i in j[APPANNIE_SALES]:
        if not 'revenue' in i['metric']:
            continue
        total += float(i['metric']['revenue'])
        print APPANNIE_AD_ACCOUNTS[i['ad_account']] + ": " + str(i['metric']['revenue'])

    print "\nTotal: " + str(total)
    curl.close()

    print "Done!"
if __name__ == '__main__':
    main()