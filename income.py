#!/usr/local/bin/python
import requests, httplib, cookielib, sys, os, re, time, argparse, calendar
from lxml import html
from datetime import date, timedelta
import pycurl, json
from StringIO import StringIO
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
APPANNIE_ACCOUNTS = [264936, 264941, 264937, 294753, 264940, 264935, 264938, 264939, 264944, 264943, 264942]
SLEEP_TIME = 30
LAST_DAYS = 7
TOTAL_ADS_INDEX = 2
GRAPH_VALUE_SIZE = 7

# Parse inputs
parser = argparse.ArgumentParser(description='Income script')
# include IAP?
parser.add_argument('-iap', default=False, required=False, dest='includeIAP', action='store_true', help='Include IAP')
# specific month?
parser.add_argument('-month', default="", required=False, help='Specific month? for example: 2016-02')
# show only today results from appannie
parser.add_argument('-onlyToday', default=False, required=False, dest='onlyToday', action='store_true', help='Show only today')

args = parser.parse_args()
includeIAP = args.includeIAP
inputMonth = args.month
month = (inputMonth if (inputMonth != "") else date.today().strftime('%Y-%m'))
firstDayOfMonth = month + "-01"
lastDayOfMonth = (month + "-" + str(calendar.monthrange(int(month.split("-")[0]), int(month.split("-")[1].lstrip("0")))[1]) if (inputMonth != "") else time.strftime("%Y-%m-%d"))
onlyToday = args.onlyToday

if (onlyToday):
    includeIAP = True

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            name, user, password = line.split()
            accounts[name] = [user, password]
    return accounts

def pageBreak():
    print "===================================="

# Get Appannie data for start until end dates
def getAppannieForDates(accounts, start, end, getIAP = True, sleepForIAP = False):
    user, password = accounts[KEYS[3]]
    b = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.WRITEFUNCTION, b.write)
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account")
    curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/ads/sales?break_down=ad_account&start_date=" + start + "&end_date=" + end)
    curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer ' + user])
    curl.perform()
    j = json.loads(b.getvalue())

    if len(j[APPANNIE_SALES]) == 0:
        curl.close()
        return False

    # prepare IAP info
    totalIAP = 0
    if (getIAP):
        for i in APPANNIE_ACCOUNTS:
            b.truncate(0)
            curl.setopt(pycurl.URL, "https://api.appannie.com/v1.2/accounts/" + str(i) + "/sales?start_date=" + start + "&end_date=" + end)
            curl.perform()
            iapj = json.loads(b.getvalue())
            try:
                if iapj['sales_list']:
                    totalIAP += (float(iapj['sales_list'][0]['revenue']['iap']['sales']) - float(iapj['sales_list'][0]['revenue']['iap']['refunds']))
            except:
                print "Caught exception: Invalid Account? " + str(i)
        if sleepForIAP:
            time.sleep(SLEEP_TIME)

    total = 0
    for i in j[APPANNIE_SALES]:
        if not 'revenue' in i['metric']:
            continue
        total += float(i['metric']['revenue'])

    curl.close()
    return [start, end, total, getIAP, totalIAP, total + totalIAP, j[APPANNIE_SALES]]

# Print Appannie data
def printAppannie(dataList):
    start, end, totalAds, printIAP, totalIAP, total, table = dataList
    print "Appannie info for " + start + " - " + end + ":"

    for i in table:
        if not 'revenue' in i['metric']:
            continue
        print APPANNIE_AD_ACCOUNTS[i['ad_account']] + ": " + str(i['metric']['revenue']) + "$"

    print "\nTotal ads: " + str(totalAds) + "$"
    if (printIAP):
        print "Total IAP: " + str(totalIAP) + "$"
    print "\nTotal: " + str(total) + "$"
    pageBreak()

def main():
    print "Income info script - by Liran Cohen V1.5"

    # Get credentials
    accounts = getCredentials(PASSWORDS_FILE)

    #Casinoland info
    print "Checking Casinoland...\n"
    user, password = accounts[KEYS[0]]
    # month = time.strftime("%Y-%m")
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
        url = "https://www.buffalopartners.com/api/revshare/traffic?username=" + user + "&apikey=" + password + "&start=" + firstDayOfMonth + "&end=" + lastDayOfMonth

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
        print KEYS[i].replace("_", " ") + "for " + month + ": "
        print "Revenue: " + root[1][-1].text + "$"
        print "Visits: " + str(visits)
        print "New opens: " + str(newOpens)
        print "Actives: " + str(actives) + "\n\n"
        pageBreak()
    pageBreak()

    #Appannie
    # Yesterday's data (or 2 days ago)
    print "Getting Appannie yesterday's data..."
    yesterdayTimeDelta = 1
    yesterday = (date.today() - timedelta(yesterdayTimeDelta)).strftime('%Y-%m-%d')
    deductFor30 = 30

    data = getAppannieForDates(accounts, yesterday, yesterday, includeIAP, (False if onlyToday else includeIAP))
    if data:
        printAppannie(data)
    else:
        yesterdayTimeDelta = 2
        yesterday = (date.today() - timedelta(yesterdayTimeDelta)).strftime('%Y-%m-%d')
        deductFor30 = 31
        data = getAppannieForDates(accounts, yesterday, yesterday, includeIAP, (False if onlyToday else includeIAP))
        printAppannie(data)

    if onlyToday:
        return

    #Get last LAST_DAYS days ads values and print graph
    print "Getting last " + str(LAST_DAYS) + " days ads results:"
    lastDays = [data[TOTAL_ADS_INDEX]]    #init with today value
    for i in range(1, LAST_DAYS):
        day = (date.today() - timedelta(yesterdayTimeDelta + i)).strftime('%Y-%m-%d')
        data = getAppannieForDates(accounts, day, day, False)
        lastDays.append(data[TOTAL_ADS_INDEX])

    sortedLastDays = sorted(lastDays, key=float, reverse=True)
    for i in sortedLastDays:
        print (str(i) + "$").rjust(GRAPH_VALUE_SIZE * (lastDays.index(i) + 1))

    # Last 30 days data
    thirtyDays = (date.today() - timedelta(deductFor30)).strftime('%Y-%m-%d')
    today = date.today().strftime('%Y-%m-%d')
    print "Getting Appannie last 30 days data (" + thirtyDays + " - " + yesterday + ")..."
    printAppannie(getAppannieForDates(accounts, thirtyDays, yesterday, includeIAP, includeIAP))

    # Data from starting of the month
    print "Getting Appannie data from the beginning of the month (" + firstDayOfMonth + " - " + lastDayOfMonth + ")..."
    printAppannie(getAppannieForDates(accounts, firstDayOfMonth, lastDayOfMonth, True))

    print "Done!"
if __name__ == '__main__':
    main()