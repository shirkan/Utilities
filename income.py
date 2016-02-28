#!/usr/local/bin/python
import requests, httplib, cookielib, sys, os, re, time, argparse
from lxml import html
from datetime import date, timedelta
import pycurl, json
from StringIO import StringIO
import xml.etree.ElementTree as ET

# Casinoland details
CASINOLAND_LOGIN_URL = "www.affiliateland.com"

# Buffalo details
BUFFALO_LOGIN_URL = "https://www.buffalopartners.com/"
BUFFALO_LOGIN_USER_ELEMENT = "UserName"
BUFFALO_LOGIN_PASSWORD_ELEMENT = "Password"
BUFFALO_LOGOUT_URL = "https://www.buffalopartners.com/login/logoff"

PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/income.password"
KEYS = ["Casinoland", "Buffalo_Main_Account", "Buffalo_Second_Account", "Appannie"]

BUFFALO_EARNINGS_CLASS = "loggedin-highlight"
APPANNIE_SALES = 'sales_list'
APPANNIE_AD_ACCOUNTS = {265056: "Applovin main", 285034: "Chartboost main", 265057: "Playhaven casino", 275073: "Playhaven beezbee", 265060: "Admob", 291338: "Vungle"}
APPANNIE_ACCOUNTS = [264936, 264941, 264937, 294753, 264940, 264935, 264938, 264939, 316870, 264944, 294479, 264943, 264942]
SLEEP_TIME = 30

# Parse inputs
parser = argparse.ArgumentParser(description='Income script')
# include IAP?
parser.add_argument('-iap', default=0, required=False, help='Include IAP?')
includeIAP = (parser.parse_args().iap == "1")

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            name, user, password = line.split()
            accounts[name] = [user, password]
    return accounts

def pageBreak():
    print "===================================="

def main():
    print "Income info script - by Liran Cohen V1.3"

    # Get credentials
    accounts = getCredentials(PASSWORDS_FILE)

    #Casinoland info
    print "Checking Casinoland...\n"
    user, password = accounts[KEYS[0]]
    month = time.strftime("%Y-%m")
    connection = httplib.HTTPSConnection(CASINOLAND_LOGIN_URL, 443)
    connection.connect()
    url = '/partners/feeds/custom_36.php?id=' + user + '&type=month_summary&month=' + month
    connection.request('GET', url)
    results = json.loads(connection.getresponse().read())['Data']
    print "Stats for: " + month
    for result in results:
        print "Tracker: " + str(result['Tracker']) + "\nVisits: " + str(result['Visits']) + "\nOpens: " + str(result['Opens']) + '\nFTDs: ' + str(result['FTDs']) + '\nDeposits: ' + \
        str(result['Deposits']) + " (euros)\nNet revenue: " + str(result['NetRevenue']) + " (euros)\nDeductions: " + str(result['Deductions']) + " (euros)\n"
        pageBreak()
    pageBreak()

    #Buffalo main account
    session_requests = requests.session()
    for i in range(1,3):
        user, password = accounts[KEYS[i]]
        url = "https://www.buffalopartners.com/api/revshare/traffic?username=" + user + "&apikey=" + password + "&start=" + time.strftime("%Y-%m-01") + "&end=" + time.strftime("%Y-%m-%d")

        result = session_requests.get(url)
        if not result.ok:
            print("ERROR! Couldn't scrape Buffalo account: " + user)
        root = ET.fromstring(result.content)
        visits = 0
        newOpens = 0
        actives = 0
        for child in root[1]:
            if child.tag == 'traffic':
                visits += int(child.attrib['visits'])
                newOpens += int(child.attrib['newOpens'])
                actives += int(child.attrib['actives'])
        print KEYS[i].replace("_", " ") + ": "
        print "Revenue: " + root[1][-1].text + "$"
        print "Visits: " + str(visits)
        print "New opens: " + str(newOpens)
        print "Actives: " + str(actives) + "\n\n"
        pageBreak()
    pageBreak()

    #Login Appannie
    print "Getting Appannie yesterday's data..."
    user, password = accounts[KEYS[3]]
    yesterday = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    deductFor30 = 30
    b = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.WRITEFUNCTION, b.write)
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account")
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + yesterday + "&end_date=" + yesterday)
    curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer ' + user])
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

    # prepare IAP info
    totalIAP = 0
    for i in APPANNIE_ACCOUNTS:
        b.truncate(0)
        curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/accounts/" + str(i) + "/sales?start_date=" + yesterday + "&end_date=" + yesterday)
        curl.perform()
        iapj = json.loads(b.getvalue())
        if iapj['sales_list']:
            totalIAP += (float(iapj['sales_list'][0]['revenue']['iap']['sales']) - float(iapj['sales_list'][0]['revenue']['iap']['refunds']))
    if includeIAP:
        time.sleep(SLEEP_TIME)

    print "Appannie info for " + yesterday + ":"
    total = 0
    for i in j[APPANNIE_SALES]:
        if not 'revenue' in i['metric']:
            continue
        total += float(i['metric']['revenue'])
        print APPANNIE_AD_ACCOUNTS[i['ad_account']] + ": " + str(i['metric']['revenue']) + "$"

    print "\nTotal ads: " + str(total) + "$"
    print "Total IAP: " + str(totalIAP) + "$"
    print "\nTotal: " + str(total + totalIAP) + "$"
    pageBreak()

    thirtyDays = (date.today() - timedelta(deductFor30)).strftime('%Y-%m-%d')
    today = date.today().strftime('%Y-%m-%d')
    print "Getting Appannie last 30 days data (" + thirtyDays + " - " + yesterday + ")..."
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + thirtyDays + "&end_date=" + today)
    curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer ' + user])
    b.truncate(0)
    curl.perform()
    j = json.loads(b.getvalue())

    # prepare IAP info
    if includeIAP:
        totalIAP = 0
        for i in APPANNIE_ACCOUNTS:
            b.truncate(0)
            curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/accounts/" + str(i) + "/sales?start_date=" + thirtyDays + "&end_date=" + today)
            curl.perform()
            iapj = json.loads(b.getvalue())
            if iapj['sales_list']:
                totalIAP += (float(iapj['sales_list'][0]['revenue']['iap']['sales']) - float(iapj['sales_list'][0]['revenue']['iap']['refunds']))
        time.sleep(SLEEP_TIME)

    total = 0
    for i in j[APPANNIE_SALES]:
        if not 'revenue' in i['metric']:
            continue
        total += float(i['metric']['revenue'])
        print APPANNIE_AD_ACCOUNTS[i['ad_account']] + ": " + str(i['metric']['revenue']) + "$"

    print "\nTotal ads: " + str(total) + "$"
    if includeIAP:
        print "Total IAP: " + str(totalIAP) + "$"
        total+=totalIAP
    print "\nTotal: " + str(total) + "$"
    pageBreak()

    beginningOfMonth = date.today().strftime('%Y-%m-01')
    print "Getting Appannie data from the beginning of the month (" + beginningOfMonth + " - " + today + ")..."
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + beginningOfMonth + "&end_date=" + today)
    curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer ' + user])
    b.truncate(0)
    curl.perform()
    j = json.loads(b.getvalue())

    # prepare IAP info
    totalIAP = 0
    for i in APPANNIE_ACCOUNTS:
        b.truncate(0)
        curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/accounts/" + str(i) + "/sales?start_date=" + beginningOfMonth + "&end_date=" + today)
        curl.perform()
        iapj = json.loads(b.getvalue())
        if iapj['sales_list']:
            totalIAP += (float(iapj['sales_list'][0]['revenue']['iap']['sales']) - float(iapj['sales_list'][0]['revenue']['iap']['refunds']))

    total = 0
    for i in j[APPANNIE_SALES]:
        if not 'revenue' in i['metric']:
            continue
        total += float(i['metric']['revenue'])
        print APPANNIE_AD_ACCOUNTS[i['ad_account']] + ": " + str(i['metric']['revenue']) + "$"

    print "\nTotal ads: " + str(total) + "$"
    print "Total IAP: " + str(totalIAP) + "$"
    print "\nTotal: " + str(total + totalIAP) + "$"
    pageBreak()

    curl.close()

    print "Done!"
if __name__ == '__main__':
    main()