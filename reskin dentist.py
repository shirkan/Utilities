#!/usr/local/bin/python3 -u
import argparse, sys, reskinutils

print("iOS dentist reskinner v1.2")

defaultVer = "1.0"

# Required arguments
parser = argparse.ArgumentParser(description='Reskin an iOS dentist game')
# game name
parser.add_argument('-name', required=True, help='Name of the game to be present on device (should be rathe short and comply with title in ASO)')
# source dir
parser.add_argument('-source', required=True, help='Source dir with assets')
# target dir (duplicated dir)
parser.add_argument('-target', required=True, help='Target dir of duplicated version')
# bundle id
parser.add_argument('-bundle', required=True, help='Bundle ID')
# IAP id
parser.add_argument('-iap', required=True, help='IAP ID convention')
# server ID
parser.add_argument('-id', required=True, help='UNIVERSE server ID')
# Flurry ID
parser.add_argument('-flurry', required=True, help='Flurry app ID')
# Version
parser.add_argument('-ver', default = defaultVer, help='Version & build number, default is ' + defaultVer)
# run or not?
parser.add_argument('-run', default=False, help='Wet run. Otherwise, just dry run (which is also default)')

args = parser.parse_args()

name = args.name
srcDir = args.source
trgDir = args.target
bundle = args.bundle
iap = args.iap
ver = args.ver
serverID = args.id
flurry = args.flurry
reskinutils.run = args.run

configFile = trgDir + "/MrDentist/Classes/Constants.h"
infoPlistFile = trgDir + "/MrDentist/Resources/Info.plist"

# FILES REPLACEMENT
# -----------------
# replace partyslots/images.xcasset/appicons
print("Replacing icons in Images.xcassets...")

dirToCopy = "/MrDentist/Images.xcassets/AppIcon.appiconset"
reskinutils.copyFilesByGlob(srcDir + dirToCopy + "/*.png", trgDir + dirToCopy)
reskinutils.checkCopy(8)
print("Done.")

# replace simpleslots/artwork/reskin
print("Replacing game assets...")

dirToCopy = "/MrDentist/Resources/Image/"
filesToCopy = ["gamescene/gameback1.png", "gamescene/gameback2.png", "gamescene/people1.png", "gamescene/people2.png", "gamescene/people3.png", "gamescene/people4.png",
"mainscene/btn_p1_u.png", "mainscene/btn_p2_u.png", "mainscene/btn_p3_u.png", "mainscene/btn_p4_u.png", "mainscene/btn_p1_d.png", "mainscene/btn_p2_d.png",
"mainscene/btn_p3_d.png", "mainscene/btn_p4_d.png", "mainscene/mainback.png", "mainscene/menuback.png"]
# gamescene: gameback1.png, gameback2.png, people1-4.png
# mainscene: btn_p1-4_d,u.png, mainback.png, menuback.png
for i in range(0, len(filesToCopy)):
	reskinutils.copyFilesByName(srcDir + dirToCopy + filesToCopy[i], trgDir + dirToCopy + filesToCopy[i])
reskinutils.checkCopy(len(filesToCopy))
print("Done.")

# END OF FILES REPLACEMENT

# CODE REPLACEMENT
# ----------------
# replace IAP
print("Replacing IAP ID...")
reskinutils.replaceInFile(configFile, "<enter_iap_id_here>", iap)
print("Done.")

# replace server ID
print("Replacing server ID...")
reskinutils.replaceInFile(configFile, "<enter_server_id_here>", serverID)
print("Done.")

# replace bundleID
print("Replacing bundle ID...")
reskinutils.replaceInFile(infoPlistFile, "enter_bundle_id_here", bundle)
print("Done.")

# replace game name
print("Replacing game name...")
reskinutils.replaceInFile(infoPlistFile, "enter_game_name_here", name)
print("Done.")

# replace version & build
print("Replacing version & build...")
reskinutils.replaceInFile(infoPlistFile, "enter_version_here", ver)
print("Done.")

# replace Flurry ID
print("Replacing flurry default ID...")
reskinutils.replaceInFile(configFile, "<enter_flurry_app_id_here>", flurry)
print("Done.")

# END OF CODE REPLACEMENT
print("Done all! Don't forget to replace 'Team' in xcode :)")
