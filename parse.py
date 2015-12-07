#!/usr/local/bin/python
import argparse,json,httplib

print "Parse create app script - by Liran Cohen V1.0"

PASSWORDS_FILE = "parse.password"

# Parse inputs
parser = argparse.ArgumentParser(description='Create parse app and retrieve info')
# account name
parser.add_argument('-account', required=True, help='Account to create game in')
# game name
parser.add_argument('-name', required=True, help='Game name')

args = parser.parse_args()
account = args.account
name = args.name

def createParseApp(name, user, password):
    print "Creating parse app " + name + " in account " + user
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('POST', '/1/apps', json.dumps({
           "appName": name,
           "clientPushEnabled" : True
         }), {
           "X-Parse-Email": user,
           "X-Parse-Password": password,
           "Content-Type": "application/json"
         })
    result = json.loads(connection.getresponse().read())
    if "applicationId" in result:
        print "App ID: " + result["applicationId"]
    else:
        print "Couldn't retrieve App ID"
        print result

    if "clientKey" in result:
        print "Client key: " + result["clientKey"]
    else:
        print "Couldn't retrieve Client Key"
        print result


def getCredentials(inputFile):
        accounts = {}
        with open(inputFile) as inFile:
            for line in inFile:
                name, user, password = line.split()
                accounts[name] = [user, password]
        return accounts

accounts = getCredentials(PASSWORDS_FILE)
if not account in accounts:
    print "Cannot find credentials for account " + account + "\n"
    print "Available accounts: " + str(accounts.keys())
else:
    user, password = accounts[account]
    createParseApp(name, user, password)

