#!/usr/local/bin/python
import sys, time, itertools, argparse, json, httplib, os, csv

# Consts
RESULTS = "50"
BASE_URL = "itunes.apple.com"
INI_FILE = os.path.dirname(os.path.realpath(__file__)) + "/aso ranking.ini"
CSV_OUTPUT_FILE = "aso ranking.csv"
DELIM = ','

# Parse inputs
parser = argparse.ArgumentParser(description='Check ASO ranking')
# account name
parser.add_argument('-lang', default="", required=False, help='Language to check')
# run or not?
parser.add_argument('-writeToFile', default=1, help='writeToFile csv file. by default 1 (yes)')

args = parser.parse_args()
lang = args.lang
writeToFile = (True if args.writeToFile == 1 else False)

def getData(inputFile):
    mainDict = {}
    subDict = {}
    sectionName = ""
    with open(inputFile) as inFile:
        for line in inFile:

            if line=="\n":
                continue

            # Check for section begin
            if line.startswith('['):

                # If we started a new section (or come up with "end"), store the previous one
                if not (sectionName == ''):
                    mainDict[sectionName] = subDict;

                sectionName = line.replace('[','').replace(']','').replace('\n','')
                subDict = {}

            # If not a new section, store data
            else:
                key, val = line.replace("\n","").split("=",1)
                subDict[key] = val
    mainDict[sectionName] = subDict
    return mainDict

def getInfoFromItunes(word, country, limit):
    connection = httplib.HTTPSConnection(BASE_URL)
    connection.connect()
    connection.request('GET', '/search?entity=software&term=' + word + '&country=' + country + '&limit=' + limit)
    results = json.loads(connection.getresponse().read())['results']
    return results

def checkPhrase(word, country, limit):
    wordToSearch = word.replace("-","%20")
    word = word.replace("-"," ")
    results = getInfoFromItunes(wordToSearch, country, limit)
    presence = []
    rank = 1

    for app in results:
        if app['artistName'] in artistNames:
            presence.append(rank)
        rank += 1
    print "Word/phrase: " + word + " has " + str(len(presence)) + " presences. Top preseneces: " + str((presence if len(presence) <=5 else presence[0:4]))
    if writeToFile:
        csvwriter.writerow([word, str(len(presence)), str((presence if len(presence) <=5 else presence[0:4]))])

def getWords(phrase):
    if not "-" in phrase:
        return [phrase]

    words = phrase.split("-")
    tuples = list(itertools.combinations(words, 2))
    for t in tuples:
        words += [("-".join(t))]
    return list(set(words + [phrase]))

def main():
    global lang, csvwriter, artistNames

    print "ASO Ranking - by Liran Cohen V1.1"
    data = getData(INI_FILE)
    artistNames = data["misc"]["artistNames"].split(",")

    if lang == "":
        print "Iterating all langs."
        langs = data["langs"].keys()
    else:
        if not lang in data["langs"]:
            print "No such language " + str(lang) + "... Available langs:\n" + str(data["langs"].keys())
            sys.exit()
        langs = [lang]

    for lang in langs:
        # Regular keywords
        words = data["keywords"][lang].split(",")
        country = data["langs"][lang]
        print "Checking lang " + lang + " for country " + country + "..."

        if writeToFile:
            csvwriter.writerow(["Lang: " + lang, "Country: " + country])
            csvwriter.writerow(["word/phrase", "preseneces", "top presences"])

        for word in words:
            wordList = getWords(word)
            for w in wordList:
                checkPhrase(w, country, RESULTS)

        # Casino keywords
        if not lang in data["casinoKeywords"]:
            continue

        words = data["casinoKeywords"][lang].split(",")
        prefix = data["casinoPrefix"][lang]
        country = data["langs"][lang]
        print "Checking casino keywords for lang " + lang + " for country " + country + "..."

        for word in words:
            wordList = getWords(word)
            for w in wordList:
                w = prefix + '-' + w
                checkPhrase(w, country, RESULTS)

    print "Done!"

if __name__ == '__main__':
    try:
        if writeToFile:
            if os.path.exists(CSV_OUTPUT_FILE):
                os.remove(CSV_OUTPUT_FILE)
            csvfile = open(CSV_OUTPUT_FILE, "w+")
            csvwriter = csv.writer(csvfile, delimiter=DELIM)
        main()
    finally:
        if writeToFile:
            csvfile.close()