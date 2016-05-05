#!/usr/local/bin/python -u
import httplib, sys, os, time, argparse, json, mandrill, slack
from datetime import date, timedelta

# Casinoland details
CHARTBOOST_BASE_URL = "analytics.chartboost.com"
# CAMPAIGNS = {
#     'adidasbloom@gmail.com' : {
#         'CASINO - Big 4' : '537b26931873da554a40103f',
#         'Casino  World - IOS' : '543a6385c26ee42f93d424cc'
#     },
#     'totemediainc@gmail.com' : {
#         'CASINO - Big 4' : '56f2550fa8b63c16e67e2438',
#         'Casino  World - IOS': '56f256ae8838095e722d9ff9'
#     }
# }
CAMPAIGNS = {
    'adidasbloom@gmail.com' : {
        'CASINO - Big 4' : '537b26931873da554a40103f',
        'Casino  World - IOS' : '543a6385c26ee42f93d424cc'
    }
}
MIN_CV = {
    'CASINO - Big 4' : 1.4,
    'Casino  World - IOS' : 1.0
}
PASSWORDS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/chartboost.password"
SLEEP_TIME = 7
SUCCESS_STATUS = "created"
CAMPAIGN_COL = 2
APP_NAME_COL = 11
APP_ID_COL = 12
APP_BUNDLE_COL = 13
COUNTRY_COL = 21
CV_COL = 23

# Parse inputs
parser = argparse.ArgumentParser(description='Income script')
# include IAP?
parser.add_argument('-dateMin', default='', required=False, dest='dateMin', help='From (YYYY-MM-DD)')
# specific month?
parser.add_argument('-dateMax', default='', required=False, dest='dateMax', help='To (YYYY-MM-DD)')
# show only today results from appannie
parser.add_argument('-yesterday', default=False, required=False, dest='yesterday', action='store_true', help='Query only yesterday')

args = parser.parse_args()
dateMin = args.dateMin
dateMax = args.dateMax
yesterday = args.yesterday

if ((not yesterday) and (dateMin == "" and dateMax == "")) or ((yesterday) and not (dateMin == "" and dateMax == "")):
    print "Please run only with -yesterday or enter from-to dates (-dateMin, -dateMax)..."
    sys.exit()

if yesterday:
    dateMin = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    dateMax = dateMin

filename = os.path.dirname(os.path.realpath(__file__)) + "/chartboost_report_" + dateMin + "_" + dateMax + ".csv"
if os.path.exists(filename):
    os.remove(filename)

def getCredentials(inputFile):
    accounts = {}
    foundSubject = False
    with open(inputFile, "r") as inFile:
        for line in inFile:
            line = line.rstrip("\n")
            if line == "" or line.startswith("#"):
                continue
            if not foundSubject and "[IDs]" not in line:
                continue
            else:
                if not foundSubject and line == "[IDs]":
                    foundSubject = True
                else:
                    if foundSubject and line.startswith("["):
                        break
            if len(line.split()) == 1:
                continue
            accounts[line.split()[0]] = { 'id' : line.split()[1], 'key' : line.split()[2] }
    return accounts

def sendJob():
    global account, userId, userSignature

    connection = httplib.HTTPSConnection(CHARTBOOST_BASE_URL, 443)
    connection.connect()
    url = '/v3/metrics/install?dateMin=' + dateMin + '&dateMax=' + dateMax + '&campaignIds=' + (",".join(CAMPAIGNS[account].values())) + '&userId=' + userId + '&userSignature=' + userSignature

    print "Sending installs request for " + account + " for date(s) " + dateMin + " - " + dateMax + "..."

    connection.request('GET', url)
    jobID = str(json.loads(connection.getresponse().read())['jobId'])
    return jobID

def checkJob(jobID, getresults = True):
    connection = httplib.HTTPSConnection(CHARTBOOST_BASE_URL, 443)
    connection.connect()
    url = '/v3/metrics/jobs/' + jobID + '?status=true'

    while True:
        print "Waiting " + str(SLEEP_TIME) + " seconds before next check..."
        time.sleep(SLEEP_TIME)
        connection.request('GET', url)
        status = str(json.loads(connection.getresponse().read())['status'])
        print "Returned status: " + status
        if status == SUCCESS_STATUS:
            break

    if getresults:
        getResults(jobID)
    return jobID

def getResults(jobID):
    global filename
    connection = httplib.HTTPSConnection(CHARTBOOST_BASE_URL, 443)
    connection.connect()
    url = '/v3/metrics/jobs/' + jobID
    connection.request('GET', url)
    results = connection.getresponse().read()
    connection.close()

    with open(filename, "a") as f:
        f.write(results)

def analyzeReport(filename):
    global account
    if not os.path.isfile(filename):
        print "No such file " + filename
        return

    toReport = {}
    idsReport = {}
    for key in CAMPAIGNS[account].keys():
        toReport[key] = []
        idsReport[key] = []

    with open(filename, "r") as f:
        inputData = (f.read().decode("utf-16"))

    readHeaders = False
    for line in inputData.split("\n"):
        lineData = line.split('\t')
        # print lineData
        if not readHeaders:
            readHeaders = True
        else:
            lineData = line.replace("\"", "").split('\t')
            if len(lineData) < CV_COL:
                continue

            campaign = lineData[CAMPAIGN_COL]
            appName = lineData[APP_NAME_COL]
            appID = lineData[APP_ID_COL]
            appBundle = lineData[APP_BUNDLE_COL]
            country = lineData[COUNTRY_COL]

            try:
                costValue = int(lineData[CV_COL])
            except ValueError:
                try:
                    costValue = float(lineData[CV_COL])
                except ValueError:
                    continue

            if costValue < MIN_CV[campaign]:
                toReport[campaign].append(appID.ljust(25) + " " + appName.ljust(40) + " " + appBundle.ljust(40) + " " + country + " " + str(costValue))
                idsReport[campaign].append(appID)

    finalReport = []
    for key in toReport.keys():
        if len(toReport[key]):
            finalReport.append("Campaign: " + key  + " (reporting installs under " + str(MIN_CV[key]) + "$)\n\n")
            for line in toReport[key]:
                finalReport.append(line + "\n")
            finalReport.append("\n")
            finalReport.append("Copaste for filtering:\n\n" + "./chartboost_filter.py -ids \"" + ", ".join(list(set(idsReport[key]))) + "\" -campaign " + CAMPAIGNS[account][key] + " -user " + account)
            finalReport.append("\n\n")

    return finalReport

def sendReport(report):
    global dateMin, dateMax

    formattedReport = []
    for acc in report.keys():
        if len(acc) != 0:
            formattedReport += [acc + ":\n", str("".join(report[acc]).encode('utf-8'))]

    if len(formattedReport) == 0:
        print "Nothing to report :)"
        return

    slack.SLsendMessageToChannel("#chartboost_report", str("".join(formattedReport)))

def main():
    print "Chartboost report script - by Liran Cohen V1.3"
    global account, userId, userSignature
    accounts = getCredentials(PASSWORDS_FILE)
    data = {}
    for account in accounts.keys():
        userId = accounts[account]['id']
        userSignature = accounts[account]['key']
        jobID = sendJob()
        checkJob(jobID)
        data[account] = analyzeReport(filename)
    sendReport(data)

    print "Last update: " + str(time.ctime())
    print "Done!"
if __name__ == '__main__':
    main()