#!/usr/local/bin/python3
import argparse, sys, reskinutils

print("Android slots reskinner v1.3")

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
reskinutils.run = args.run

# Files
androidManifestFile = trgDir + "/AndroidManifest.xml"
androidManifestBinFile = trgDir + "/bin/AndroidManifest.xml"
stringsFile = trgDir + "/res/values/strings.xml"
serverManagerFile = trgDir + "/src/com/appninja/serveradsmanager/ServerManager.java"
bigCasinoSlotsActivityFile = trgDir + "/src/com/appninja/slots/BigCasinoSlotsActivity.java"
receiverFile = trgDir + "/src/com/appninja/slots/Receiver.java"
mainMenuLayerFile = trgDir + "/src/com/awesomegames/bigcasinoslots/Layers/MainMenuLayer.java"
javaFiles = trgDir + "/src/com/*/*/*.java"
javaFiles2 = trgDir + "/src/com/*/*/*/*.java"

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
		reskinutils.copyFilesByGlob(srcAssets + "/game" + str(i) + "*.png", trgAssets)
	reskinutils.checkCopy(2*(4+3))
	print("Done.")

	# replace reels
	print("Replacing reels assets...")
	reelsDict = ["gems", "horse", "mega", "slot"]
	for i in range(0, len(reelsDict)):
		reskinutils.copyFilesByGlob(srcAssets + "/" + reelsDict[i] + "*.png", trgAssets)
	reskinutils.checkCopy(len(reelsDict) * 10)
	for i in range(0, len(reelsDict)):
		reskinutils.copyTree(srcAssets + "/" + reelsDict[i], trgAssets + "/" + reelsDict[i])
	reskinutils.checkCopy(len(reelsDict))
	print("Done.")

	# replace icons
	print("Replacing icons...")
	iconsDict = ["drawable-hdpi/icon.png", "drawable-mdpi/icon.png", "drawable-xhdpi/icon.png"]
	for i in range(0, len(iconsDict)):
		reskinutils.copyFilesByGlob(srcRes + "/" + iconsDict[i], trgRes + "/" + iconsDict[i])
	reskinutils.checkCopy(len(iconsDict))
	print("Done.")


	# CODE REPLACEMENT
	# ----------------
	# replace game name
	print("Replacing game name...")
	reskinutils.replaceInFile(stringsFile, "enter_game_name_here", name)
	reskinutils.replaceInFile(receiverFile, "enter_game_name_here", name)
	print("Done.")

	# replace bundleID
	print("Replacing bundle ID...")
	reskinutils.replaceInFile(androidManifestFile, "enter_bundle_id_here", bundle)
	reskinutils.replaceInFile(androidManifestBinFile, "enter_bundle_id_here", bundle)
	reskinutils.replaceInFileByGlob(javaFiles, "enter_bundle_id_here", bundle)
	reskinutils.replaceInFileByGlob(javaFiles2, "enter_bundle_id_here", bundle)
	print("Done.")

	# replace server ID
	print("Replacing server ID...")
	reskinutils.replaceInFile(serverManagerFile, "enter_server_id_here", serverID)
	print("Done.")

	# replace BASE_KEY for IAP
	print("Replacing BASE KEY...")
	reskinutils.replaceInFile(bigCasinoSlotsActivityFile, "enter_base_key_here", basekey)
	print("Done.")
	
	# replace initial coins
	print("Replacing initial coins to " + str(coins) + "...")
	reskinutils.replaceInFile(mainMenuLayerFile, "enter_initial_coins_here", str(coins))
	print("Done.")

	# END OF CODE REPLACEMENT
	sys.exit("Done all!")

sys.exit("Nothing to do...")
