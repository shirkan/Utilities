#!/usr/bin/ruby
require "spaceship"
require "date"

# Consts
NONE = "none"
INI_SETUP_FILE = "appstore.ini"

module TYPES
    SLOTS = "Slots"
    DENTIST = "Dentist"
end
GAMES_TYPES = [TYPES::SLOTS, TYPES::DENTIST]

CHECK_BUILDS_ON_STATUS = "Prepare for Submission"

module APPSTATUS
    NOT_EXIST = 0
    LIVE = 1
    EDITABLE = 2
    LIVE_EDITABLE = 3
end

module MENUTITLE
    NO_TITLE = 0
    GENERAL_TITLE = 1
    ACCOUNT_TITLE = 2
    APPS_TITLE = 3
end

# Menu consts
MAIN_MENU_OPTIONS = { "----- MAIN MENU -----" => MENUTITLE::GENERAL_TITLE,
    "Select account & app" => "selectAccountAndApp",
    "Select account" => "selectAccount",
    "Select app" => "selectApp",
    "Accounts status (contol table, takes several minutes...)" => "accountsStatus",
    "----- ACCOUNT MENU -----" => MENUTITLE::ACCOUNT_TITLE,
    "Create new app in account" => "createNewApp",
    "Update app in account (fill in what's new in all languages)" => "updateApp",
    "----- APPS MENU -----" => MENUTITLE::APPS_TITLE,
    "Set first version details (Use this to fix *NEW* apps only!)" => "updateNewAppVersion",
    "Create IAP template" => "createIAPTemplate",
    "Change app type" => "selectType",
    "Keywords menu" => "keywordsMenu",
    "Titles menu" => "titlesMenu",
    "Log out from account" => "logout",
    "Exit" => "exit"
}

KEYWORDS_MENU_OPTIONS = { "Get current keywords" => "getKeywords",
    "Update generic keywords" => "updateGenericKeywords",
    "Update keywords from file" => "updateKeywordsFromFile"
}

TITLES_MENU_OPTIONS = { "Get current titles" => "getTitles",
    "Update one title for all languages" => "updateTitleToAllLanguages",
    "Update titles from file" => "updateTitlesFromFile"
}

# Globals
$currLogin = { "currAccount" => NONE,
    "currApp" => NONE,
    "currAppName" => NONE,
    "currAppID" => NONE,
    "currBundleID" => NONE,
    "currAppType" => NONE
}

$today = Date.today()

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
        dict[currSubject] = hash if currSubject != ""
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
        when "bold"
            "\e[1m#{msg}\e[0m"
        when "pink"
            "\e[35m#{msg}\e[0m"
        when "red"
            "\e[31m#{msg}\e[0m"
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
    puts "Current logged account: " + $currLogin["currAccount"]
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

    if $currLogin["currAccount"] == selectedAccount
        puts "Already logged in with #{$currLogin["currAccount"]}. Refresh connection? (y/[n])"
        option = gets.chomp()
        if option == "y" or option == "Y"
            puts "Refreshing connection..."
            login(selectedAccount, accounts[selectedAccount])
        end
    else
        if $currLogin["currAccount"] != NONE
            logout()
        end

        login(selectedAccount, accounts[selectedAccount])
    end
end

# Set current app
def setCurrentApp(app, name, apple_id, bundle_id, type)
    $currLogin["currApp"] = app
    $currLogin["currAppName"] = name
    $currLogin["currAppID"] = apple_id
    $currLogin["currBundleID"] = bundle_id
    $currLogin["currAppType"] = type
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

    setCurrentApp(Spaceship::Tunes::Application.find(all_apps[option].apple_id), all_apps[option].name, all_apps[option].apple_id, all_apps[option].bundle_id, NONE)
    selectType()
end

# login
def login(user, pass)
    puts "Logging in ITC & Developer Portal with account #{user}..."
    Spaceship::Portal.login(user, pass)
    Spaceship::Tunes.login(user, pass)
    $currLogin["currAccount"] = user
end

# logout
def logout()
    $currLogin.each_key {|k| $currLogin[k] = NONE}
end

# exit
def exit()
    abort("Bye! :)")
end

# Check account
def checkAccount(printMsg = true)
    if $currLogin["currAccount"] == NONE
        putsc "Please login with an account first", "e" if printMsg
        return false
    end
    return true
end

# Get Statuses of all accounts
def accountsStatus()
    puts "Saving the following output also to #{$config["misc"]["saveTableToFile"]}..."
    f = File.open($config["misc"]["saveTableToFile"], "w")

    $config["accounts"].each do |user,pass|
        puts "Account #{user}:"
        f.puts("Account #{user}:")
        dict = {}
        liveApps = 0
        login(user, pass)
        apps = Spaceship::Tunes::Application.all

        apps.each do |app|
            if appStatus(app) == APPSTATUS::LIVE
                liveApps+=1
                next
            end

            v = app.edit_version
            status = "#{app.name} : "
            if v.app_status == CHECK_BUILDS_ON_STATUS
                status += v.app_status + " (#{v.version}) "
                buildsStatus = ""
                builds = v.candidate_builds
                builds.each {|b| buildsStatus+="#{b.build_version} (#{b.train_version}) " + (b.processing ? "Processing... |" : " Ready to use! |")}
                status += buildsStatus == "" ? "No builds" : buildsStatus

                if defined? builds[0].processing && !builds[0].processing
                    v.select_build(builds[0])
                    status += " #{builds[0].build_version} was selected."
                end
            else
                status += (v.app_status != nil ? v.app_status : v.raw_status) + " (#{v.version})"
            end

            puts status
            f.puts(status)

        end
        # print total apps + how many are live
        puts "Total #{apps.count} Applications, #{liveApps} are solely live, #{apps.count-liveApps} are being edited"
        f.puts("Total #{apps.count} Applications, #{liveApps} are solely live, #{apps.count-liveApps} are being edited")
        pageBreak()
        f.puts("--------------------------------------------------")
    end

    f.close()
end

# Check app
def checkApp(printMsg = true)
    if $currLogin["currApp"] == NONE
        putsc "Please select app first", "e" if printMsg
        return false
    end
    return true
end

# Get keywords
def getKeywords()
    v = appIsEditable($currLogin["currApp"]) ? $currLogin["currApp"].edit_version : $currLogin["currApp"].live_version
    puts v.keywords()
end

# Update keywords in app
def updateKeywords(keywordsList)
    v = $currLogin["currApp"].edit_version

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
def updateGenericKeywords()
    if !appIsEditable($currLogin["currApp"])
        putsc "Cannot update keywords of live apps", "e"
        return
    end

    type = $currLogin["currAppType"]
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
    if !appIsEditable($currLogin["currApp"])
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
    names = $currLogin["currApp"].details.name

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

    details = $currLogin["currApp"].details
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
    selectType()
    type = $currLogin["currAppType"]
    keepTrying = true
    configData = $config["new#{type}"]

    while keepTrying do
        begin
            puts "Enter app name:"
            name = gets.chomp()

            bundleID = "com.#{$currLogin["currAccount"].split("@")[0]}.#{name.downcase.gsub(" ","")}"
            puts "Enter bundle id (default is #{bundleID}):"
            inputBundle = gets.chomp()
            inputBundle = bundleID if inputBundle == ""

            sku = configData["sku"].concat("_#{$today.day}#{$today.month}#{$today.year}")
            lang = configData["primaryLangauge"]
            version = configData["version"]

            # Create new app identifier in Developer Portal
            puts "Creating a new app with name #{name} and bundle id #{inputBundle}..."
            portalApp = Spaceship.app.create!(bundle_id: inputBundle, name: name)

            # Only slots - need to upload CSR and create push norifications

            # Create new app entry on ITC
            puts "Register a new app on ITC with the following details:\nName: #{name}\nBundle ID: #{inputBundle}\nSKU: #{sku}\nPrimary language: #{lang}\nVersion: #{version}"
            app = Spaceship::Tunes::Application.create!(name: name, primary_language: lang, version: version, sku: sku, bundle_id: inputBundle)
            setCurrentApp(app, name, app.apple_id, inputBundle, type)

            # Set price tier
            appUpdatePriceTier($currLogin["currApp"], configData["priceTier"])

            # Set categories
            puts "Updating categories"
            appUpdateCatergories($currLogin["currApp"], configData)

            # Upload screenshots

            # Upload icon

            # Edit version
            updateNewAppVersion()

            # Process completed
            keepTrying = false
        rescue => e
            putsc "Caught exception: #{e}\n\nPlease fix and retry.", "e"
            setCurrentApp(NONE, NONE, NONE, NONE, NONE)
        end
        break if !keepTrying
    end
end

# Open app to update
def updateApp()
    currStatus = appStatus($currLogin["currApp"])
    if currStatus == APPSTATUS::NOT_EXIST or currStatus == APPSTATUS::EDITABLE
        putsc "#{$currLogin["currAppName"]} has no live versions and cannot be updated.", "e"
        return
    end

    type = $currLogin["currAppType"]

    # we need to create a new version
    if currStatus == APPSTATUS::LIVE
        puts "Creating new version..."
        currVer = $currLogin["currApp"].live_version.version
        major,minor = currVer.split(".")
        minor = minor.to_i + 1
        newVer = "#{major}.#{minor}"
        puts "Current version is #{currVer}, opening a new version #{newVer}..."
        $currLogin["currApp"].create_version!(newVer)
    else
        puts "Already has an editable version..."
    end

    # prepare bullets
    puts "Preparing bullets..."
    data = $config["update#{type}"]
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
    v = $currLogin["currApp"].edit_version
    v.release_notes.keys.each do |lang|
        v.release_notes[lang] = bullets
    end

    # save
    puts "Saving app info on ITC..."
    v.save!
    puts "Done."
end

# Update new app details
def updateNewAppVersion()
    app = $currLogin["currApp"]
    type = $currLogin["currAppType"]
    config = $config["new#{type}"]

    puts "Updating version info for type #{type} (support URL, copyright, rating, review details, localizations, descriptions, keywords)..."
    puts "Don't forget to mark made for kids on ITC!!" if type == TYPES::DENTIST
    v = app.edit_version

    # Set support URL
    v.support_url.keys.each {|k| v.support_url[k] = config["supportURL"]}

    # Set copyright
    v.copyright = config["copyright"]

    # Set marketing URL
    v.marketing_url = config["marketingURL"]

    # Set rating
    v.update_rating( Hash[$config["itunesCriterias"]["ratings"].zip config["rating"].map! {|k| k.to_i}] )

    # Set review details
    v.review_email = $currLogin["currAccount"]
    v.review_first_name = config["reviewFirstName"][rand(config["reviewFirstName"].length)]
    v.review_last_name = config["reviewLastName"][rand(config["reviewLastName"].length)]
    v.review_phone_number = config["reviewPhonePrefix"] + rand().to_s().split(".",2)[1][1..config["reviewPhoneDigits"].to_i]

    # Open langauges in new ver and place descriptions & keywords
    v.create_languages(config["localizations"])
    config["localizations"].each do |lang|
        v.description[lang] = config["description"].gsub("\\n","\n")
        v.keywords[lang] = $config["generic#{type}Keywords"][lang] if defined? $config["generic#{type}Keywords"][lang]
    end

    v.save!
    puts "Done saving details on ITC."
end

#Create IAP template page
def createIAPTemplate()
    filename = "#{$currLogin["currAppName"]}.iap.txt"
    f = File.open(filename, "w")

    config = $config["new#{$currLogin["currAppType"]}"]
    sku = appGetSKU($currLogin["currApp"])

    puts "Creating IAP template in file \"#{filename}\""

    # Write headers
    f.puts($config["itunesCriterias"]["iapHeaders"].join("\t"))

    for i in 0..config["iapProducts"].length-1
        prodId = "#{$currLogin["currBundleID"]}.#{config["iapProducts"][i]}"
        f.puts("#{sku}\t#{prodId}\t#{config["iapProducts"][i]}\t#{config["iapTypes"][i]}\tyes\t#{config["iapPriceTiers"][i]}\t#{config["iapProducts"][i]}\t#{config["iapDescriptions"][i]}\t#{config["iapScreenshotPath"]}")
    end

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

def appUpdatePriceTier(app, tier)
    puts "Updating tier..."
    app.update_price_tier!(tier)
end

def appUpdateCatergories(app, config)
    puts "Updating categories..."
    details = app.details
    details.primary_category = config["primaryCategory"]
    details.primary_first_sub_category = config["primaryFirstSubCategory"]
    details.primary_second_sub_category = config["primarySecondSubCategory"]
    details.secondary_category = config["secondaryCategory"]
    details.save!
end

def appGetSKU(app)
    return app.vendor_id
end
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Menu functions

# Print headers
def printHeaders()
    # headers
        puts "Current logged account: " + $currLogin["currAccount"]
        puts "Current selected app: " + $currLogin["currAppName"]
        puts "Current app type: " + $currLogin["currAppType"] if $currLogin["currAppType"] != NONE
end

# App status
def printAppStatus()
    return if !checkApp(false)
    appIsEditable($currLogin["currApp"]) ? (putsc "App is editable", "blink") : (putsc "App is live", "pink")
    puts ""
end

# Print menu
def showMenu(dict, backOption=true)
    printHeaders()
    printAppStatus() if !backOption

    funcs = dict.clone()

    # menu
    length = dict.length-1
    j=0
    color = "regular"
    for i in 0..length
        case dict[dict.keys[i]]
        when MENUTITLE::GENERAL_TITLE
            putsc "#{dict.keys[i]}", "bold"
            funcs.delete(dict.keys[i])

        when MENUTITLE::ACCOUNT_TITLE
            color = $currLogin["currAccount"] == NONE ? "red" : "bold"
            putsc "#{dict.keys[i]}", color
            color = "regular" if color == "bold"
            funcs.delete(dict.keys[i])

        when MENUTITLE::APPS_TITLE
            color = $currLogin["currApp"] == NONE ? "red" : "bold"
            putsc "#{dict.keys[i]}", color
            color = "regular" if color == "bold"
            funcs.delete(dict.keys[i])

        else
            putsc "[#{j.to_s.rjust(2)}] - #{dict.keys[i]}", color
            j+=1
        end
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

    eval(funcs[funcs.keys[option]])
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

# Titles menu
def titlesMenu()
    loop do
        return if !checkAccount or !checkApp
        break if !showMenu(TITLES_MENU_OPTIONS)
    end
end

# Select type
def selectType()
    pageBreak()
    puts "Select type:"

    for i in 0..GAMES_TYPES.length-1
        putsc "[#{i.to_s.rjust(1)}] - #{GAMES_TYPES[i]}"
    end

    puts "Select option:"
    option = readNumber(0, GAMES_TYPES.length-1)
    $currLogin["currAppType"] = GAMES_TYPES[option]
end

# ------------------------------------------------

# Begin script
puts "Appstore Control Center V1.7 - By Liran Cohen"
init()
pageBreak()
mainMenu()

# first keywords, then upload screenshots then titles