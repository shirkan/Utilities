import argparse, shutil, glob, fileinput, sys

print("iOS reskinner v1.1")

# Required arguments
parser = argparse.ArgumentParser(description='Reskin an iOS slot machine')
# game name
parser.add_argument('-name', required=True, help='Name of the game to be present on device (should be rathe short and comply with title in ASO)')
# source dir
parser.add_argument('-source', required=True, help='Source dir with assets')
# target dir (duplicated dir)
parser.add_argument('-target', required=True, help='Target dir of duplicated version')
# bundle id
parser.add_argument('-bundle', required=True, help='Bundle ID')
# leaderboard id
parser.add_argument('-leaderboard', required=True, help='Leaderboard ID')
# IAP id
parser.add_argument('-iap', required=True, help='IAP ID convention')
# server ID
parser.add_argument('-id', required=True, help='UNIVERSE server ID')
# run or not?
parser.add_argument('-run', help='Wet run. Otherwise, just dry run')

args = parser.parse_args()

name = args.name
srcDir = args.source
trgDir = args.target
bundle = args.bundle
leaderboard = args.leaderboard
iap = args.iap
serverID = args.id
run = args.run

configFile = trgDir + "/SimpleSlots/configure.h"
serverFile = trgDir + "/SimpleSlots/ServerManager.m"
infoPlistFile = trgDir + "/SimpleSlots/PartySlots-Info.plist"

# Generic copying validation by number of files to copy
def checkCopy(itemsToCopy, itemsCopied):
	if itemsCopied != itemsToCopy:
		exitMsg = "Invalid number of copied items! Copied " + str(itemsCopied) + " Should be " + str(itemsToCopy)
		sys.exit(exitMsg)

# Copy files by full name
def copyFilesByName(source, target):
	global itemsCopied, run
	print("Copying " + source + " to " + target)
	itemsCopied+=1
	if run:
		shutil.copy(source, target)


# Copy files by globbing
def copyFilesByGlob(source, target):
	global itemsCopied, run
	for file in glob.glob(source):
	    print("Copying globbed " + file + " to " + target)
	    itemsCopied+=1
	    if run:
	    	shutil.copy(file, target)

# Copy entire tree (folder)
def copyTree(source, target):
	global itemsCopied, run
	print("Copying tree " + source + " to " + target)
	itemsCopied+=1
	if run:
		shutil.rmtree(target)
		shutil.copytree(source, target)

# Replace "replacewhat" in fileToEdit with "replaceWith"
def replaceInFile(fileToEdit, replaceWhat, replaceWith):
	global run
	if run:
	with fileinput.FileInput(fileToEdit, inplace=True, backup='.bak') as file:
	    for line in file:
	        print(line.replace(replaceWhat, replaceWith), end='')

# FILES REPLACEMENT
# -----------------
# replace all icons in main dir
print("Replacing icons on main dir...")

itemsCopied = 0
copyFilesByGlob(srcDir + "/AppIcon*.png", trgDir)
copyFilesByGlob(srcDir + "/iTunesArtwork*.png", trgDir)
copyFilesByName(srcDir + "/icon-ipad.png", trgDir)
copyFilesByName(trgDir + "/iTunesArtwork@2x.png", trgDir + "/icon1024.png")

checkCopy(18,itemsCopied)
itemsCopied = 0
print("Done.")

# replace partyslots/images.xcasset/appicons
print("Replacing icons in Images.xcassets...")

dirToCopy = "/PartySlots/Images.xcassets/AppIcon.appiconset"
copyFilesByGlob(srcDir + "/AppIcon*.png", trgDir + dirToCopy)
copyFilesByGlob(srcDir + "/iTunesArtwork*.png", trgDir + dirToCopy)
copyFilesByName(srcDir + "/icon-ipad.png", trgDir + dirToCopy)
copyFilesByName(trgDir + dirToCopy + "/AppIcon29x29.png", trgDir + dirToCopy + "/AppIcon29x29-1.png")
copyFilesByName(trgDir + dirToCopy + "/AppIcon29x29@2x.png", trgDir + dirToCopy + "/AppIcon29x29@2x-1.png")
copyFilesByName(trgDir + dirToCopy + "/AppIcon40x40@2x.png", trgDir + dirToCopy + "/AppIcon40x40@2x-1.png")
copyFilesByName(trgDir + dirToCopy + "/iTunesArtwork@2x.png", trgDir + dirToCopy + "/icon1024.png")

checkCopy(21,itemsCopied)
itemsCopied = 0
print("Done.")

# replace simpleslots/artwork/reskin
print("Replacing reskin assets in artwork...")

dirToCopy = "/SimpleSlots/artwork/reskin"
copyTree(srcDir + dirToCopy, trgDir + dirToCopy)

checkCopy(1,itemsCopied)
itemsCopied = 0
print("Done.")

# replace simpleslots/artwork/icon*
print("Replacing icons on assets dir...")

srcIconFiles = ["/AppIcon57x57.png", "/AppIcon57x57@2x.png", "/AppIcon72x72.png", "/AppIcon72x72@2x.png"]
trgIconFiles = ["/SimpleSlots/artwork/icon.png", "/SimpleSlots/artwork/icon@2x.png", "/SimpleSlots/artwork/icon-ipad.png", "/SimpleSlots/artwork/icon-ipad@2x.png"]

for i in range(0, len(srcIconFiles)):
	copyFilesByName(srcDir + srcIconFiles[i], trgDir + trgIconFiles[i])

checkCopy(4,itemsCopied)
itemsCopied = 0
print("Done.")

# END OF FILES REPLACEMENT

# CODE REPLACEMENT
# ----------------
# replace leaderboard
print("Replacing leaderboard ID...")

if run:
	with fileinput.FileInput(configFile, inplace=True, backup='.bak') as file:
	    for line in file:
	        print(line.replace("<enter_leaderboard_id_here>", leaderboard), end='')

print("Done.")

# replace IAP
print("Replacing IAP ID...")

if run:
	with fileinput.FileInput(configFile, inplace=True, backup='.bak') as file:
	    for line in file:
	        print(line.replace("<enter_iap_id_here>", iap), end='')

print("Done.")

# replace server ID
print("Replacing server ID...")

if run:
	with fileinput.FileInput(serverFile, inplace=True, backup='.bak') as file:
	    for line in file:
	        print(line.replace("<enter_server_id_here>", serverID), end='')

print("Done.")

# replace bundleID
print("Replacing bundle ID...")

if run:
	with fileinput.FileInput(infoPlistFile, inplace=True, backup='.bak') as file:
	    for line in file:
	        print(line.replace("enter_bundle_id_here", bundle), end='')

print("Done.")

# replace game name
print("Replacing game name...")
replaceInFile(infoPlistFile, "enter_game_name_here", name)
# if run:
# 	with fileinput.FileInput(infoPlistFile, inplace=True, backup='.bak') as file:
# 	    for line in file:
# 	        print(line.replace("enter_game_name_here", name), end='')

print("Done.")

# END OF CODE REPLACEMENT
print("Done all! Don't forget to replace 'Team' in xcode :)")
