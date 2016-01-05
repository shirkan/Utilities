#!/usr/local/bin/python3
import argparse, sys, reskinutils, os, random, time
from random import randint
from reskinutils import reskinPrint
from collections import OrderedDict

print("ALDG - Android Long Description Generator v1.1")

# Consts
PLACEHOLDER = "!@#"     # a const for placeholder
DEFAULT_LANG = "en-us"  # default language
MAX_REPITATIONS_PER_KEYWORD = 2     # max times of repitations per keyword

# Define globals
SECTIONS = ["Opening", "KeywordsContent", "GenericContent", "NoRealMoney", "DownloadNow", "Features", "BottomLine", "end"]    # define sections
dataDict = {}   # dictionary which contains sentences from dict file
pickedDict = {}     # dictionary which contain picked sentences
description = ""    # final description

# Parse inputs
parser = argparse.ArgumentParser(description='Generate a long description for an android game based on dictionaries')
# language
parser.add_argument('-lang', default=DEFAULT_LANG, help='Language to generate description for. must have a dictionary file named aldg.<lang>.dict present. Default is ' + DEFAULT_LANG)
# keywords
parser.add_argument('-keywords', required=True, help='A list of keywords to place in placeholders, separated by commas')
# picks list
parser.add_argument('-picks', required=True, help='List of numbers which represent how many sentences to pick from each section for the following sections: ' + str(SECTIONS[0:len(SECTIONS)-1]))
# output method
parser.add_argument('-output', default="", help='Output the description to screen (default, leave empty to do so), or to file with specified name')

args = parser.parse_args()

keywords = args.keywords.split(',')
picks = args.picks.split(',')
lang = args.lang
output = args.output


# Load data from dictionary files
def readDict(lang=""):
    global SECTIONS, dataDict

    dictFile = "aldg." + lang + ".dict"
 #    dictFile = "tmp.py"

    if not os.path.isfile(dictFile):
        reskinPrint("Cannot load dictionary, file not exists: " + dictFile , "e")
        return False
    else:
        reskinPrint("Found dictionary file " + dictFile)

    with open(dictFile) as inFile:
        sectionName = ""
        sentences = []
        for line in inFile:

            # Check for section begin
            if line.startswith('['):

    			# If we started a new section (or come up with "end"), store the previous one
                if not (sectionName == ''):
                    dataDict[sectionName] = sentences;

                sectionName = line.replace('[','').replace(']','').replace('\n','')
                sentences = []

    			# Verify section name is valid
                if not sectionName in SECTIONS:
                    reskinPrint("Invalid section " + sectionName + ", skipping..."  , "w")
                    sectionName = ''

                continue

    		# If not a new section, store sentence
            sentences.append(line.replace('\n',''))
    return True

def selectSentences():
    global picks, SECTIONS, pickedDict, dataDict

    # iterate how many picks to do in each section
    for howmany, section in zip(picks, SECTIONS):
        pickedList = []
        howmany = int(howmany)
        while howmany > 0:
            pick = randint(0, len(dataDict[section])-1)

            if pick in pickedList:
                continue
            else:
                if not section in pickedDict:
                    pickedDict[section] = []
                pickedDict[section].append(dataDict[section][pick])
                pickedList.append(pick)

            howmany-=1
            del dataDict[section][pick]

            # check if we have snetences left
            if len(dataDict[section]) == 0:
                reskinPrint('Picked all sentences from section ' + section + '...', 'w')
                break

def joinDescription():
    global description, SECTIONS

    for section in SECTIONS[0:-1]:
            for sentence in pickedDict[section]:
                description += sentence + " "
            description += "\n\n"

def replaceWords():
    global picks, description

    # prepare a bucket dict to count how many times we used each keyword
    totalReplacementsLeft = len(keywords) * MAX_REPITATIONS_PER_KEYWORD     # count how many replacements were done since we don't care which word to choose if all words replaced max times
    bucketDict = OrderedDict();
    for word in keywords:
        bucketDict[word] = 0

    while PLACEHOLDER in description:
        # draw a word
        random.seed(time.time())
        word = keywords[randint(0, len(keywords) - 1)]
        while (totalReplacementsLeft > 0) and (bucketDict[word] == MAX_REPITATIONS_PER_KEYWORD):
            word = keywords[randint(0, len(keywords) - 1)]

        description = description.replace(PLACEHOLDER, word, 1)
        bucketDict[word] += 1
        totalReplacementsLeft -= 1
        if totalReplacementsLeft == 0:
            reskinPrint("All keywords were placed " + str(MAX_REPITATIONS_PER_KEYWORD) + " times... randomly placing.")


def outputDescription():
    global output, description

    reskinPrint("Printing description...")
    if output == "":
        print(description)
    else:
        outputFile = open(output, "w")
        outputFile.write(description)
        outputFile.close()


readDict(lang)
selectSentences()
joinDescription()
replaceWords()
outputDescription()




# Generate long description




# how to play
# features
# faq
# about us