#!/usr/local/bin/python3
import argparse, shutil, glob, fileinput, sys

print("Android slots reskinner v1.2")

defaultCoins = 5000

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
# BASE KEY for IAP
parser.add_argument('-basekey', required=True, help='BASE KEY for IAP selling')
# # leaderboard id
# parser.add_argument('-leaderboard', required=True, help='Leaderboard ID')
# Coins
parser.add_argument('-coins', default = defaultCoins, help='Initial coins amount, default is ' + str(defaultCoins))
# server ID
parser.add_argument('-id', required=True, help='UNIVERSE server ID')
# run or not?
parser.add_argument('-run', help='Wet run. Otherwise, just dry run')

# Arguments
args = parser.parse_args()
name = args.name
srcDir = args.source
trgDir = args.target
bundle = args.bundle
# leaderboard = args.leaderboard
basekey = args.basekey
coins = args.coins
serverID = args.id
run = args.run

# Files
androidManifestFile = trgDir + "/AndroidManifest.xml"
androidManifestBinFile = trgDir + "/bin/AndroidManifest.xml"
stringsFile = trgDir + "/res/values/strings.xml"
serverManagerFile = trgDir + "/src/com/appninja/serveradsmanager/ServerManager.java"
bigCasinoSlotsActivityFile = trgDir + "/src/com/appninja/slots/BigCasinoSlotsActivity.java"
mainMenuLayerFile = trgDir + "/src/com/awesomegames/bigcasinoslots/Layers/MainMenuLayer.java"
javaFiles = trgDir + "/src/com/*/*/*.java"
javaFiles2 = trgDir + "/src/com/*/*/*/*.java"

# Variables
itemsCopied = 0

# Generic copying validation by number of files to copy
def checkCopy(itemsToCopy):
	global itemsCopied
	if itemsCopied != itemsToCopy:
		sys.exit("Invalid number of copied items! Copied " + str(itemsCopied) + " Should be " + str(itemsToCopy))
	itemsCopied = 0

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
		with fileinput.FileInput(fileToEdit, inplace=True) as file:
			for line in file:
				print(line.replace(replaceWhat, replaceWith), end='')

# Replace "replacewhat" in globbed filesToEdit with "replaceWith"
def replaceInFileByGlob(filesToEdit, replaceWhat, replaceWith):
	global run
	for globbedFile in glob.glob(filesToEdit):
		print("Editing globbed file " + globbedFile)
		with fileinput.FileInput(globbedFile, inplace=True) as file:
			for line in file:
				if run:
					print(line.replace(replaceWhat, replaceWith), end='')


if __name__ == '__main__':
	# FILES REPLACEMENT
	# -----------------

	srcAssets = srcDir + "/assets"
	trgAssets = trgDir + "/assets"
	srcRes = srcDir + "/res"
	trgRes = trgDir + "/res"

	# replace worlds
	print("Replacing worlds assets...")
	for i in range(1,5):
		copyFilesByGlob(srcAssets + "/game" + str(i) + "*.png", trgAssets)
	checkCopy(2*(4+3))
	print("Done.")

	# replace reels
	print("Replacing reels assets...")
	reelsDict = ["gemsitem*.png", "horseitem*.png", "megaitem*.png", "slotitem*.png"]
	for i in range(0, len(reelsDict)):
		copyFilesByGlob(srcAssets + "/" + reelsDict[i], trgAssets)
	checkCopy(len(reelsDict) * 10)
	print("Done.")

	# replace icons
	print("Replacing icons...")
	iconsDict = ["drawable-hdpi/icon.png", "drawable-mdpi/icon.png", "drawable-xhdpi/icon.png"]
	for i in range(0, len(iconsDict)):
		copyFilesByGlob(srcRes + "/" + iconsDict[i], trgRes + "/" + iconsDict[i])
	checkCopy(len(iconsDict))
	print("Done.")


	# CODE REPLACEMENT
	# ----------------
	# replace game name
	print("Replacing game name...")
	replaceInFile(stringsFile, "enter_game_name_here", name)
	print("Done.")

	# replace bundleID
	print("Replacing bundle ID...")
	replaceInFile(androidManifestFile, "enter_bundle_id_here", bundle)
	replaceInFile(androidManifestBinFile, "enter_bundle_id_here", bundle)
	replaceInFileByGlob(javaFiles, "enter_bundle_id_here", bundle)
	replaceInFileByGlob(javaFiles2, "enter_bundle_id_here", bundle)
	print("Done.")

	# replace server ID
	print("Replacing server ID...")
	replaceInFile(serverManagerFile, "enter_server_id_here", serverID)
	print("Done.")

	# replace BASE_KEY for IAP
	print("Replacing BASE KEY...")
	replaceInFile(bigCasinoSlotsActivityFile, "enter_base_key_here", basekey)
	print("Done.")
	
	# replace initial coins
	print("Replacing initial coins to " + str(coins) + "...")
	replaceInFile(mainMenuLayerFile, "enter_initial_coins_here", str(coins))
	print("Done.")



	# END OF CODE REPLACEMENT
	sys.exit("Done all!")

sys.exit("Nothing to do...")
