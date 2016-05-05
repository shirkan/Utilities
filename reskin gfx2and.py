#!/usr/local/bin/python3 -u
import argparse, sys, reskinutils, os

print("Graphics 2 Android slots reskinner v1.1")

defaultCoins = 5000

# Required arguments
parser = argparse.ArgumentParser(description='Reskin an iOS slot machine')
# game name
parser.add_argument('-name', required=True, help='Name of the game to be present on device (should be rathe short and comply with title in ASO)')
# assets dir
parser.add_argument('-assets', required=True, help='Graphics dir with assets (worlds & reels)')
# icons dir
parser.add_argument('-icons', required=True, help='Icons dir')
# target dir (duplicated dir)
parser.add_argument('-target', required=True, help='Target dir of duplicated version')
# bundle id
parser.add_argument('-bundle', required=True, help='Bundle ID')
# BASE KEY for IAP
parser.add_argument('-basekey', required=True, help='BASE KEY for IAP selling')
# Coins
parser.add_argument('-coins', default = defaultCoins, help='Initial coins amount, default is ' + str(defaultCoins))
# server ID
parser.add_argument('-id', required=True, help='UNIVERSE server ID')
# run or not?
parser.add_argument('-run', help='Wet run. Otherwise, just dry run')

# Arguments
args = parser.parse_args()
name = args.name
assets = args.assets
icons = args.icons
trgDir = args.target
bundle = args.bundle
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

	trgAssets = trgDir + "/assets"
	trgRes = trgDir + "/res"

	# replace worlds
	print("Replacing worlds assets...")
	reskinutils.copyFilesByGlob(assets + "/LevelSelect/game*@2x.*", trgAssets)
	reskinutils.checkCopy(2*4 + 2)
	print("Done.")

	# replace reels
	print("Replacing reels assets...")
	reelsDict = ["gems", "horse", "mega", "slot"]
	assetsDict = ["7", "A", "bonus", "diamond", "J", "K", "lemon", "Q", "star", "wild"]
	# copy lvl[i]/lvl[i]item_<asset_name>@2x.png to <reels_name>item_<asset_name_title>@2x.png & <reels_name>/<asset_name_title>_<reels_name>.png
	for i in range(0, len(reelsDict)):
		for j in range(0, len(assetsDict)):
			fileToCopy = assets + "/lvl" + str(i+1) + "/lvl" + str(i+1) + "item_" + assetsDict[j] + "@2x.png"
			if not (os.path.isfile(fileToCopy)):
				print("Cannot find " + fileToCopy + ", trying to capitalizing asset name...")
				fileToCopy = assets + "/lvl" + str(i+1) + "/lvl" + str(i+1) + "item_" + assetsDict[j].title() + "@2x.png"
				if not (os.path.isfile(fileToCopy)):
					sys.exit("Cannot find " + assets + "/lvl" + str(i+1) + "/lvl" + str(i+1) + "item_" + assetsDict[j] + "@2x.png or " + fileToCopy)

			reskinutils.copyFilesByName(fileToCopy, trgAssets + "/" + reelsDict[i] + "item_" + assetsDict[j].title() + "@2x.png")
			reskinutils.copyFilesByName(fileToCopy, trgAssets + "/" + reelsDict[i] + "/" + assetsDict[j].title() + "_" + reelsDict[i] +".png")
	reskinutils.checkCopy(len(reelsDict) * len(assetsDict) * 2)
	print("Done.")

	# replace icons
	print("Replacing icons...")
	# 72 x 72, 57 x 57, 144 x 144
	sizesDict = ["72x72", "57x57", "72x72@2x"]
	iconsDict = ["drawable-hdpi/icon.png", "drawable-mdpi/icon.png", "drawable-xhdpi/icon.png"]
	for i in range(0, len(iconsDict)):
		reskinutils.copyFilesByGlob(icons + "/AppIcon" + sizesDict[i] + ".png", trgRes + "/" + iconsDict[i])
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
