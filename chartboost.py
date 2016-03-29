#!/usr/local/bin/python
import httplib, sys, os, time, argparse, json, mandrill
from datetime import date, timedelta

# Casinoland details
CHARTBOOST_BASE_URL = "analytics.chartboost.com"
CAMPAIGNS = {
    'CASINO - Big 4' : '537b26931873da554a40103f',
    'Casino  World - IOS' : '543a6385c26ee42f93d424cc'
}
MIN_CV = {
    'CASINO - Big 4' : 2.5,
    'Casino  World - IOS' : 1.5
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
parser.add_argument('-dateMin', default='', required=False, dest='dateMin', action='store_true', help='From (YYYY-MM-DD)')
# specific month?
parser.add_argument('-dateMax', default='', required=False, dest='dateMax', action='store_true', help='To (YYYY-MM-DD)')
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

filename = "chartboost_report_" + dateMin + "_" + dateMax + ".csv"

def getCredentials(inputFile):
    accounts = {}
    with open(inputFile) as inFile:
        for line in inFile:
            return line.split()

def sendJob():
    global userId, userSignature

    connection = httplib.HTTPSConnection(CHARTBOOST_BASE_URL, 443)
    connection.connect()
    url = '/v3/metrics/install?dateMin=' + dateMin + '&dateMax=' + dateMax + '&campaignIds=' + (",".join(CAMPAIGNS.values())) + '&userId=' + userId + '&userSignature=' + userSignature

    print "Sending installs request for " + dateMin + " - " + dateMax + "..."

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

    with open(filename, "w") as f:
        f.write(results)

def analyzeReport(filename):
    if not os.path.isfile(filename):
        print "No such file " + filename
        return

    toReport = {}
    for key in CAMPAIGNS.keys():
        toReport[key] = []

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
                costValue = float(lineData[CV_COL])

            # print appID + " " + appName + " (" + appBundle + ") from " + country + " with cost value of " + str(costValue)

            if costValue < MIN_CV[campaign]:
                toReport[campaign].append(appID + " " + appName + " (" + appBundle + ") from " + country + " with cost value of " + str(costValue))

    finalReport = []
    for key in toReport.keys():
        if len(toReport[key]):
            finalReport.append("Campaign: " + key  + " (reporting installs under " + str(MIN_CV[key]) + "$)\n\n")
            for line in toReport[key]:
                finalReport.append(line + "\n")
            finalReport.append("\n")

    return finalReport

def sendReport(report):
    global dateMin, dateMax

    if len(report) == 0:
        print "Nothing to report :)"
        return

    mandrill_client = mandrill.Mandrill('78MeL8wSNNw6CkhRDnQzlw')
    message = {
        'from_email' : 'automator@totemedia.co',
        'from_name' : 'Chartboost Stalker',
        'subject' : 'Chartboost Cost Value Report for ' + dateMin + ' - ' + dateMax,
        'to': [{'email': 'totemediainc@gmail.com',
                'name': 'Totemedia Inc.',
                'type': 'to'}],
        'text' : str("".join(report))
    }

    print "Sending report by mail..."
    result = mandrill_client.messages.send(message=message)[0]['status']
    print "Status is: " + str(result)

def main():
    print "Chartboost script - by Liran Cohen V1.0"
    global userId, userSignature
    userId, userSignature = getCredentials(PASSWORDS_FILE)
    jobID = sendJob()
    checkJob(jobID)
    sendReport(analyzeReport(filename))

    print "Last update: " + str(time.ctime())
    print "Done!"
if __name__ == '__main__':
    main()