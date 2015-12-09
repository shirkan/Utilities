#!/usr/bin/ruby
require "spaceship"

# Consts
NONE = "none"
INI_SETUP_FILE = "appstore.ini"

module TYPES
    SLOTS = "SLOTS"
    DENTIST = "DENTIST"
end
GAMES_TYPES = [TYPES::SLOTS, TYPES::DENTIST]

module APPSTATUS
    NOT_EXIST = 0
    LIVE = 1
    EDITABLE = 2
    LIVE_EDITABLE = 3
end



# Menu consts
MAIN_MENU_OPTIONS = { "Select account & app" => "selectAccountAndApp",
    "Select account" => "selectAccount",
    "Select app" => "selectApp",
    "Keywords menu" => "keywordsMenu",
    "Titles menu" => "titlesMenu",
    "Create new app in account" => "createNewAppInAccount",
    "Update app in account (fill in what's new in all languages)" => "updateInAccount",
    "Log out from account" => "logout",
    "Exit" => "exit"
}

KEYWORDS_MENU_OPTIONS = { "Get current keywords" => "getKeywords",
    "Update generic keywords" => "keywordsUpdateMenu",
    "Update keywords from file" => "updateKeywordsFromFile"
}

TITLES_MENU_OPTIONS = { "Get current titles" => "getTitles",
    "Update one title for all languages" => "updateTitleToAllLanguages",
    "Update titles from file" => "updateTitlesFromFile"
}

UPDATE_GENERIC_KEYWORDS_OPTIONS = { "Slots" => "updateGenericKeywords(TYPES::SLOTS)",
    "Dentist" => "updateGenericKeywords(TYPES::DENTIST)"
}

CREATE_NEW_APP_OPTIONS = { "Slots" => "createNewApp(TYPES::SLOTS)",
    "Dentist" => "createNewApp(TYPES::DENTIST)"
}

UPDATE_APP_OPTIONS = { "Slots" => "updateApp(TYPES::SLOTS)",
    "Dentist" => "updateApp(TYPES::DENTIST)"
}

# Globals
$currAccount = NONE
$currApp = NONE
$currAppName = NONE
$currAppID = NONE
$currBundleID = NONE

# Data globals
$config = Hash.new

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Utilities functions

# Read dictionary from file
def readDictFromFile(file, delim = "=")
    dict = Hash.new
    hash = Hash.new
    currSubject = ""
    File.open(file, "r") do |f|
        f.each_line do |line|
            line = line.chomp

            # skip empty lines or comments
            next if line == "" or line.start_with?("#")

            # catch subjects
            if line.start_with?("[")
                dict[currSubject] = hash if currSubject != ""
                currSubject = line.sub('[','').sub(']','')
                hash = Hash.new
            else
                key, value = line.split(delim,2)
                value = value.sub('[','').sub(']','').split(", ") if value.start_with?("[")
                hash[key] = value
            end
        end
    end
    return dict
end

# Print page break
def pageBreak()
    puts "------------------------------------------------\n"
end

# Print override
def printOverride(msg)
    print "#{msg}\r"
    # $stdout.flush
end

# print in color
def putsc (msg, type = "i")
    puts case type
        when "w"
            "\e[33m#{msg}\e[0m"
        when "e"
            "\e[31m#{msg}\e[0m"
        when "blink"
            "\e[5m#{msg}\e[0m"
        when "pink"
            "\e[35m#{msg}\e[0m"
        else
            msg
    end
end

# read number
def readNumber(from = 0, to = 9)
    ok = false
    num = gets.chomp()
    loop do
        # check if number
        if !num.match(/^(\d)+$/)
            putsc "Not a number!", "e"
        else
            num = num.to_i

            # check if in range
            if num < from or num > to
                putsc "#{num} is not in the range of #{from} - #{to}", "e"
            else
                ok = true
            end
        end
        break if ok
        num = gets.chomp()
    end
    num
end

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Core functions

# Init
def init()
    $config = readDictFromFile(INI_SETUP_FILE)
    $stdout.sync = true
end

def selectAccountAndApp()
    selectAccount()
    selectApp()
end

# Select account
def selectAccount()
    pageBreak()
    puts "Current logged account: " + $currAccount
    puts "Select account: "
    accounts = $config["accounts"]
    keys = accounts.keys

    for i in 0..keys.length-1
        puts "[#{i.to_s.rjust(2)}] - #{keys[i]}"
    end
    puts "[#{keys.length.to_s.rjust(2)}] - Back"

    option = readNumber(0, keys.length)
    if option == accounts.keys.length
        return
    end

    selectedAccount = keys[option]

    if $currAccount == selectedAccount
        puts "Already logged in with #{$currAccount}. Refresh connection? (y/[n])"
        option = gets.chomp()
        if option == "y" or option == "Y"
            puts "Refreshing connection..."
            login(selectedAccount, accounts[selectedAccount])
        end
    else
        if $currAccount != NONE
            logout()
        end

        $currAccount = selectedAccount
        puts "Logging in appstore with account #{$currAccount}..."
        login(selectedAccount, accounts[selectedAccount])
    end
end

# Select app
def selectApp()
    return if !checkAccount()

    puts "Retreiving apps list..."
    all_apps = Spaceship::Tunes::Application.all
    puts "Select app:"
    puts "[ #] -   App ID   -                           Bundle ID                          - App name"
    for i in 0..all_apps.length-1
        puts "[#{i.to_s.rjust(2)}] - #{all_apps[i].apple_id} - #{all_apps[i].bundle_id.ljust(60)} - #{all_apps[i].name}"
    end
    puts "[#{all_apps.length.to_s.rjust(2)}] - Back"

    option = readNumber(0, all_apps.length)
    if option == all_apps.length
        return
    end

    $currAppName = all_apps[option].name
    $currAppID =  all_apps[option].apple_id
    $currBundleID = all_apps[option].bundle_id
    $currApp = Spaceship::Tunes::Application.find($currAppID)
end

# login
def login(user, pass)
    Spaceship::Tunes.login(user, pass)
end

# logout
def logout()
    $currAccount = NONE
    $currApp = NONE
    $currAppName = NONE
    $currAppID = NONE
    $currBundleID = NONE
end

# exit
def exit()
    abort("Bye! :)")
end

# Check account
def checkAccount(printMsg = true)
    if $currAccount == NONE
        putsc "Please login with an account first", "e" if printMsg
        return false
    end
    return true
end

# Check app
def checkApp(printMsg = true)
    if $currApp == NONE
        putsc "Please select app first", "e" if printMsg
        return false
    end
    return true
end

# Get keywords
def getKeywords()
    v = appIsEditable($currApp) ? $currApp.edit_version : $currApp.live_version
    puts v.keywords()
end

# Update keywords in app
def updateKeywords(keywordsList)
    v = $currApp.edit_version

    i = 1
    skipped = 0
    for lang, keywordsLang in keywordsList
        printOverride("#{lang} - #{i}/#{keywordsList.length} (#{skipped} skipped)")
        begin
            # print "#{lang} (#{i}/#{keywordsList.length}), "
            v.keywords[lang] = keywordsLang
        rescue RuntimeError
            puts "Skipping #{lang}..."
            skipped+=1
        end
        i+=1
    end

    puts "\nSaving app info..."
    v.save!

    puts "Done."
end

# Update keywords from generic keywords files
def updateGenericKeywords(type)
    if !appIsEditable($currApp)
        putsc "Cannot update keywords of live apps", "e"
        return
    end

    if !GAMES_TYPES.include?(type)
        putsc "No such type #{type}"
        return
    end

    typeKeywords = $config["generic#{type}Keywords"]
    puts "Updating keywords for type #{type} in #{typeKeywords.length} localizations..."
    updateKeywords(typeKeywords)
end

# Update keywords from custom keywords files
def updateKeywordsFromFile()
    if !appIsEditable($currApp)
        putsc "Cannot update keywords of live apps", "e"
        return
    end

    # Get file, select default if empty
    puts "Enter file to read keywords from (default: #{$config["default"]["keywordsInputFile"]}):"
    inputFile = gets.chomp()
    inputFile = $config["default"]["keywordsInputFile"] if inputFile == ""

    keywordsList = readDictFromFile(inputFile)
    updateKeywords(keywordsList)
end

# Get titles
def getTitles()
    names = $currApp.details.name

    #workaround for now
    originalNames = names.original_array
    for i in 0..originalNames.length-1
        lang = originalNames[i]["localeCode"]
        puts "#{lang.ljust(7)}: #{names[lang]}"
    end
end

# Update the same title for all languages
def updateTitleToAllLanguages()
    puts "Please enter title to update in all languages:"
    title = gets.chomp()

    details = $currApp.details
    names = details.name
    #workaround for now
    originalNames = names.original_array

    puts "You are going to replace #{originalNames.length} languages title with #{title} - Are you sure you want to continue? (y/[n])"
    option = gets.chomp()
    if option == 'y' or option == 'Y'
        for i in 0..originalNames.length-1
            lang = originalNames[i]["localeCode"]
            details.name[lang] = title
        end

        puts "Replacing titles & saving app info..."
        details.save!
        puts "Done."
    end
end

# Create new app
def createNewApp()
end

# Open app to update
def updateApp(type)
    currStatus = appStatus($currApp)
    if currStatus == APPSTATUS::NOT_EXIST or currStatus == APPSTATUS::EDITABLE
        putsc "#{$currAppName} has no live versions and cannot be updated.", "e"
        return
    end

    # we need to create a new version
    if currStatus == APPSTATUS::LIVE
        puts "Creating new version..."
        currVer = $currApp.live_version.version
        major,minor = currVer.split(".")
        minor = minor.to_i + 1
        newVer = "#{major}.#{minor}"
        puts "Current version is #{currVer}, opening a new version #{newVer}..."
        $currApp.create_version!(newVer)
    else
        puts "Already has an editable version..."
    end

    # prepare bullets
    puts "Preparing bullets..."
    data = $config[(type == TYPES::SLOTS ? "updateSlots" : "updateDentist")]
    bullets = data["mustBullets"]
    bulletDict = data["optionalBullets"]
    bulletsLeft = data["numberOfBullets"].to_i - bullets.length

    while bulletsLeft>0 and bulletDict.length>0 do
        bullets.unshift(bulletDict.delete_at(rand(bulletDict.length)))
        bulletsLeft-=1
    end

    bullets = data["bulletPrefix"] + bullets.join("\n#{data["bulletPrefix"]}")
    puts "'What's new' is going to be filled with the following bullets:\n#{bullets}"

    # fill in bullets in all what's new languages
    puts "Filling what's new in all languages..."
    v = $currApp.edit_version
    v.release_notes.keys.each do |lang|
        v.release_notes[lang] = bullets
    end

    # save
    puts "Saving app info..."
    v.save!
    puts "Done."
end


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Appstore utilities

# app is editable
def appIsEditable(app)
    return app.edit_version != nil
end

def appStatus(app)
    return (appIsEditable(app) ? (app.live_version != nil ? APPSTATUS::LIVE_EDITABLE : APPSTATUS::EDITABLE ) : (app.live_version != nil ? APPSTATUS::LIVE : APPSTATUS::NOT_EXIST ))
end

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Menu functions

# Print headers
def printHeaders()
    # headers
        puts "Current logged account: " + $currAccount
        puts "Current selected app: " + $currAppName
end

# App status
def printAppStatus()
    return if !checkApp(false)
    appIsEditable($currApp) ? (putsc "App is editable", "blink") : (putsc "App is live", "pink")
    puts ""
end

# Print menu
def showMenu(dict, backOption=true)
    printHeaders()
    printAppStatus() if !backOption

    # menu
    length = dict.length-1
    for i in 0..length
        puts "[#{i.to_s.rjust(2)}] - #{dict.keys[i]}"
    end

    if backOption
        length += 1
        puts "[#{length.to_s.rjust(2)}] - Back"
    end

    puts "Select option:"
    option = readNumber(0, length)

    if backOption and option == length
        return false
    end

    eval(dict[dict.keys[option]])
    pageBreak()
    return true
end

# Main menu
def mainMenu()
    loop do
        showMenu(MAIN_MENU_OPTIONS,false)
    end
end

# Keywords menu
def keywordsMenu()
    loop do
        return if !checkAccount or !checkApp
        break if !showMenu(KEYWORDS_MENU_OPTIONS)
    end
end

def keywordsUpdateMenu()
    showMenu(UPDATE_GENERIC_KEYWORDS_OPTIONS)
end

# Titles menu
def titlesMenu()
    loop do
        return if !checkAccount or !checkApp
        break if !showMenu(TITLES_MENU_OPTIONS)
    end
end

# Create new app in account
def createNewAppInAccount()
    return if !checkAccount
    showMenu(CREATE_NEW_APP_OPTIONS)
end

# Update app in account
def updateInAccount()
    return if !checkAccount or !checkApp
    showMenu(UPDATE_APP_OPTIONS)
end

# ------------------------------------------------

# Begin script
puts "Appstore Control Center V1.3 - By Liran Cohen"
init()
pageBreak()
mainMenu()

# first keywords, then upload screenshots then titles