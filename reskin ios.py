#!/usr/local/bin/python3
import argparse, sys, reskinutils

print("iOS slots reskinner v1.3")

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
reskinutils.run = args.run

configFile = trgDir + "/SimpleSlots/configure.h"
serverFile = trgDir + "/SimpleSlots/ServerManager.m"
infoPlistFile = trgDir + "/SimpleSlots/PartySlots-Info.plist"

# FILES REPLACEMENT
# -----------------
# replace all icons in main dir
print("Replacing icons on main dir...")

reskinutils.copyFilesByGlob(srcDir + "/AppIcon*.png", trgDir)
reskinutils.copyFilesByGlob(srcDir + "/iTunesArtwork*.png", trgDir)
reskinutils.copyFilesByName(srcDir + "/icon-ipad.png", trgDir)
reskinutils.copyFilesByName(trgDir + "/iTunesArtwork@2x.png", trgDir + "/icon1024.png")
reskinutils.checkCopy(18)
print("Done.")

# replace partyslots/images.xcasset/appicons
print("Replacing icons in Images.xcassets...")

dirToCopy = "/PartySlots/Images.xcassets/AppIcon.appiconset"
reskinutils.copyFilesByGlob(srcDir + "/AppIcon*.png", trgDir + dirToCopy)
reskinutils.copyFilesByGlob(srcDir + "/iTunesArtwork*.png", trgDir + dirToCopy)
reskinutils.copyFilesByName(srcDir + "/icon-ipad.png", trgDir + dirToCopy)
reskinutils.copyFilesByName(trgDir + dirToCopy + "/AppIcon29x29.png", trgDir + dirToCopy + "/AppIcon29x29-1.png")
reskinutils.copyFilesByName(trgDir + dirToCopy + "/AppIcon29x29@2x.png", trgDir + dirToCopy + "/AppIcon29x29@2x-1.png")
reskinutils.copyFilesByName(trgDir + dirToCopy + "/AppIcon40x40@2x.png", trgDir + dirToCopy + "/AppIcon40x40@2x-1.png")
reskinutils.copyFilesByName(trgDir + dirToCopy + "/iTunesArtwork@2x.png", trgDir + dirToCopy + "/icon1024.png")
reskinutils.checkCopy(21)
print("Done.")

# replace simpleslots/artwork/reskin
print("Replacing reskin assets in artwork...")

dirToCopy = "/SimpleSlots/artwork/reskin"
reskinutils.copyTree(srcDir + dirToCopy, trgDir + dirToCopy)
reskinutils.checkCopy(1)
print("Done.")

# replace simpleslots/artwork/icon*
print("Replacing icons on assets dir...")

srcIconFiles = ["/AppIcon57x57.png", "/AppIcon57x57@2x.png", "/AppIcon72x72.png", "/AppIcon72x72@2x.png"]
trgIconFiles = ["/SimpleSlots/artwork/icon.png", "/SimpleSlots/artwork/icon@2x.png", "/SimpleSlots/artwork/icon-ipad.png", "/SimpleSlots/artwork/icon-ipad@2x.png"]

for i in range(0, len(srcIconFiles)):
	reskinutils.copyFilesByName(srcDir + srcIconFiles[i], trgDir + trgIconFiles[i])
reskinutils.checkCopy(4)
print("Done.")

# END OF FILES REPLACEMENT

# CODE REPLACEMENT
# ----------------
# replace leaderboard
print("Replacing leaderboard ID...")
reskinutils.replaceInFile(configFile, "<enter_leaderboard_id_here>", leaderboard)
print("Done.")

# replace IAP
print("Replacing IAP ID...")
reskinutils.replaceInFile(configFile, "<enter_iap_id_here>", iap)
print("Done.")

# replace server ID
print("Replacing server ID...")
reskinutils.replaceInFile(serverFile, "<enter_server_id_here>", serverID)
print("Done.")

# replace bundleID
print("Replacing bundle ID...")
reskinutils.replaceInFile(infoPlistFile, "<enter_bundle_id_here>", bundle)
print("Done.")

# replace game name
print("Replacing game name...")
reskinutils.replaceInFile(infoPlistFile, "enter_game_name_here", name)
print("Done.")

# END OF CODE REPLACEMENT
print("Done all! Don't forget to replace 'Team' in xcode :)")
