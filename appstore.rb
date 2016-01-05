#!/usr/bin/ruby
require "spaceship"
require "date"
require "credentials_manager"

# Consts
NONE = "none"
INI_SETUP_FILE = "/Users/Shirkan/Github/AppNinjaz/Utilities/appstore.ini"

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
    "Account status" => "accountStatus($currLogin[\"currAccount\"], $config[\"accounts\"][$currLogin[\"currAccount\"]])",
    "Display credentials" => "displayCredentials",
    "Log out from account" => "logout",
    "----- APPS MENU -----" => MENUTITLE::APPS_TITLE,
    "Set first version details (Use this to fix *NEW* apps only!)" => "updateNewAppVersion",
    "Update default descriptions & keywords" => "updateDefaultDescriptionAndKeywords",
    "Create push notification certificate & p12 file" => "createPushNotification",
    "Create & download provisioning file" => "createProvisioningFile",
    "Create IAP template" => "createIAPTemplate",
    "Remove all localizations" => "removeAllLocalizations",
    "Change app type" => "selectType",
    "Keywords menu" => "keywordsMenu",
    "Titles menu" => "titlesMenu",
    "Upload icon" => "uploadIcon",
    "Upload screenshots" => "uploadScreenshots",
    "Update price tier" => "appUpdatePriceTier",
    "Update app categories" => "appUpdateCatergories",
    "----- BUILDS MENU -----" => MENUTITLE::APPS_TITLE,
    "Create a new build for compilation" => "createNewBuild",
    "Create flurry ID" => "createFlurryID",
    "Create universe server ID" => "createUniverseID",
    "Create Parse app ID & client key" => "createParse",
    "Select latest build" => "selectLatestBuild",
    "Submit for review" => "submitForReview",
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
    "currBundleID" => NONE,
    "currAppType" => NONE
}

$currIDs = { "flurry" => NONE,
    "universe" => NONE,
    "parseAppID" => NONE,
    "parseClientKey" => NONE
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
def readNumber(from = 0, to = 9, allowBlank = false)
    ok = false
    num = gets.chomp().rstrip
    loop do
        return num if num == "" and allowBlank

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
    return num
end

# execute process and return output
def execute(cmd)
    puts "Running #{cmd}"
    res = %x[#{cmd} 2>&1].chomp()
    puts res
    return res
end

# Read file or dir
def readFile(msg, isDir = false)
    path = ""
    loop do
        puts msg
        path = gets.chomp()
        return "0" if path == "0"
        path = path.sub("~", File.expand_path("~")).rstrip.gsub('\\',"")

        next if not File.exists?(path)

        # Check dir correctness
        if isDir and not File.directory?(path)
            putsc "No such directory #{path}", "e"
            next
        end

        # Check file correctness
        if not isDir and not File.file?(path)
            putsc "No such file #{path}", "e"
            next
        end

        break
    end
    return path
end

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Core functions

# Init
def init()
    $config = readDictFromFile(INI_SETUP_FILE)
    $stdout.sync = true

    # Refresh credentials manager
    $config["accounts"].each do |user,pass|
        CredentialsManager::AccountManager.new(user: user, password: pass)
    end
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

def displayCredentials()
    puts "Account name: #{$currLogin["currAccount"]}\nPassword: #{$config["accounts"][$currLogin["currAccount"]]}"
end

# Set current app
def setCurrentApp(app, name, bundle_id, type)
    $currLogin["currApp"] = app
    $currLogin["currAppName"] = name
    $currLogin["currBundleID"] = bundle_id
    $currLogin["currAppType"] = type
    $currIDs.each_key {|k| $currIDs[k] = NONE}
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

    setCurrentApp(Spaceship::Tunes::Application.find(all_apps[option].apple_id), all_apps[option].name, all_apps[option].bundle_id, NONE)
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
    $currIDs.each_key {|k| $currIDs[k] = NONE}
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
        accountStatus(user, pass, f)
    end

    f.close()
end

# print account status, outputFileDescriptor should be already opened (a descriptor)
def accountStatus(user, pass, outputFileDescriptor=nil)
    puts "Account #{user}:"
    outputFileDescriptor.puts("Account #{user}:") if not outputFileDescriptor.nil?
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
            status += v.app_status + " (#{v.version}) - "
            buildsStatus = ""
            builds = v.candidate_builds
            builds.each {|b| buildsStatus+="#{b.build_version} (#{b.train_version}) " + (b.processing ? "Processing... |" : " Ready to use! |")}
            status += buildsStatus == "" ? "No builds" : buildsStatus[0..-3]

            if defined? builds[0].processing and !builds[0].processing
                v.select_build(builds[0])
                status += " #{builds[0].build_version} was selected."
                v.save!
            end
        else
            status += ((not v.app_status.nil?) ? v.app_status : v.raw_status).capitalize() + " (#{v.version})"
        end

        status += " (Slots)" if ["casino", "slot"].any? {|x| app.name.downcase.include?(x)}
        status += " (Dentist)" if ["dentist", "clinic"].any? {|x| app.name.downcase.include?(x)}

        puts status
        outputFileDescriptor.puts(status) if not outputFileDescriptor.nil?

    end
    # print total apps + how many are live
    puts "Total #{apps.count} Applications, #{liveApps} are solely live, #{apps.count-liveApps} are being edited"
    outputFileDescriptor.puts("Total #{apps.count} Applications, #{liveApps} are solely live, #{apps.count-liveApps} are being edited") if not outputFileDescriptor.nil?
    pageBreak()
    outputFileDescriptor.puts("--------------------------------------------------") if not outputFileDescriptor.nil?
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
    # Get file, select default if empty
    inputFile = readFile("Enter file to read keywords from (default: #{$config["defaults"]["keywordsInputFile"]}) or 0 to get back:")
    inputFile = $config["defaults"]["keywordsInputFile"] if inputFile == ""
    return if inputFile == "0"

    keywordsList = readDictFromFile(inputFile)
    updateKeywords(keywordsList["keywords"])
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

def updateTitles(titlesList)
    puts titlesList
    details = $currLogin["currApp"].details
    names = details.name
    #workaround for now
    originalNames = names.original_array

    skipped = 0
    changed = 0

    for i in 0..originalNames.length-1
        lang = originalNames[i]["localeCode"]
        if not titlesList.has_key?(lang)
            puts "Cannot find a title for #{lang}, skipping"
            skipped+=1
            next
        end
        details.name[lang] = titlesList[lang]
        changed+=1
    end

    puts "Total skips: #{skipped}."
    if changed > 0
        puts "\nSaving app info..."
        details.save!
    end

    puts "Done."
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

def updateTitlesFromFile()
    # Get file, select default if empty
    inputFile = readFile("Enter file to read titles from (default: #{$config["defaults"]["titlesInputFile"]}) or 0 to get back:")
    inputFile = $config["defaults"]["titlesInputFile"] if inputFile == ""
    return if inputFile == "0"

    titlesList = readDictFromFile(inputFile)
    updateTitles(titlesList["titles"])
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
            app = Spaceship.app.create!(bundle_id: inputBundle, name: name)

            # Create new app entry on ITC
            puts "Registering a new app on ITC with the following details:\nName: #{name}\nBundle ID: #{inputBundle}\nSKU: #{sku}\nPrimary language: #{lang}\nVersion: #{version}"
            itcApp = Spaceship::Tunes::Application.create!(name: name, primary_language: lang, version: version, sku: sku, bundle_id: inputBundle)
            setCurrentApp(app, name, inputBundle, type)

            puts "App created succesfully on ITC and Developers Portal, no errors should occur now..."

            # Only slots - need to upload CSR and create push norifications, download provisioning file
            createPushNotification() if type == TYPES::SLOTS
            createProvisioningFile() if type == TYPES::SLOTS

            #Set price tier
            appUpdatePriceTier($currLogin["currApp"], configData["priceTier"])

            # Set categories
            appUpdateCatergories($currLogin["currApp"], configData)

            # Upload icon
            uploadIcon()

            # Upload screenshots
            uploadScreenshots()

            puts "current app: #{$currLogin["currApp"]} \npress enter to continue"
            ppp = gets()

            # Edit version
            updateNewAppVersion()

            # Update descriptions and keywords
            updateDefaultDescriptionAndKeywords()

            # Create IAP template
            createIAPTemplate()

            # Process completed
            keepTrying = false
        rescue => e
            putsc "Caught exception: #{e}\n\nPlease fix and retry.", "e"
            setCurrentApp(NONE, NONE, NONE, NONE)
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

    puts "Updating version info for type #{type} (support URL, copyright, rating, review details)..."
    puts "Don't forget to mark made for kids on ITC!!" if type == TYPES::DENTIST
    v = app.edit_version

    # Set support URL
    v.support_url.keys.each {|k| v.support_url[k] = config["supportURL"]}

    # Set copyright
    v.copyright = config["copyright"]

    # Set marketing URL
    v.marketing_url.keys.each {|k| v.marketing_url[k] = config["marketingURL"]}

    # Set rating
    v.update_rating( Hash[$config["itunesCriterias"]["ratings"].zip config["rating"].map! {|k| k.to_i}] )

    # Set review details
    v.review_email = $currLogin["currAccount"]
    v.review_first_name = config["reviewFirstName"][rand(config["reviewFirstName"].length)]
    v.review_last_name = config["reviewLastName"][rand(config["reviewLastName"].length)]
    loop do
        phoneSucceed = false
        begin
            v.review_phone_number = config["reviewPhonePrefix"] + rand().to_s().split(".",2)[1][1..config["reviewPhoneDigits"].to_i]
            puts "Trying to use phone number #{v.review_phone_number}..."
            v.save!
            phoneSucceed = true
            puts "Phone number ok - Saved!"
        rescue => e
            putsc "Caught exception: #{e}\n\nRetrying...", "e"
        end
        break if phoneSucceed
    end
  end

def updateDefaultDescriptionAndKeywords()
    app = $currLogin["currApp"]
    type = $currLogin["currAppType"]
    config = $config["new#{type}"]
    v = app.edit_version

    # Open langauges in new ver and place descriptions & keywords
    puts "Creating localizations..."
    v.create_languages(config["localizations"])
    v.save!

    puts "Placing default description & keywords..."
    config["localizations"].each do |lang|
        v.description[lang] = config["description"].gsub("\\n","\n")
        puts "for lang #{lang}     placing #{$config["generic#{type}Keywords"][lang]}"
        v.keywords[lang] = $config["generic#{type}Keywords"][lang]
    end

    puts "Saving details..."
    v.save!
    puts "Done saving details on ITC."
end

#Create IAP template page
def createIAPTemplate()
    filename = "#{$currLogin["currAppName"]}.iap.txt"
    puts "Enter bundle ID for IAP (default is #{$currLogin["currBundleID"]}):"
    bundleID = gets().chomp()
    bundleID = $currLogin["currBundleID"] if bundleID == ""

    puts "Creating IAP template for #{$currLogin["currAppName"]} in file #{filename}"

    f = File.open(filename, "w")

    config = $config["new#{$currLogin["currAppType"]}"]
    sku = appGetSKU($currLogin["currApp"])

    # Write headers
    f.puts($config["itunesCriterias"]["iapHeaders"].join("\t"))

    for i in 0..config["iapProducts"].length-1
        prodId = "#{bundleID}.#{config["iapProducts"][i]}"
        f.puts("#{sku}\t#{prodId}\t#{config["iapProducts"][i]}\t#{config["iapTypes"][i]}\tyes\t#{config["iapPriceTiers"][i]}\t#{config["iapProducts"][i]}\t#{config["iapDescriptions"][i]}\t#{config["iapScreenshotPath"]}")
    end

    f.close()

    puts "Done."
end

def removeAllLocalizations()
    puts "You are going to remove all localiztions - Are you sure you want to continue? (y/[n])"
    option = gets.chomp()
    if option == 'y' or option == 'Y'
        app = $currLogin["currApp"]
        v = app.edit_version
        v.languages = []

        puts "Removing localizations..."
        v.save!
    end
end

def uploadIcon()
    if not appIsEditable($currLogin["currApp"])
        putsc "App is not editable!", "e"
        return
    end

    path = readFile("Enter full path of icon file (1024x1024) or type 0 to skip")
    return if path == "0"

    puts "Uploading icon from #{path}..."
    v = $currLogin["currApp"].edit_version
    v.upload_large_icon!(path)
    puts "Saving app info on ITC... "
    v.save!
end

def uploadScreenshots()
    if not appIsEditable($currLogin["currApp"])
        putsc "App is not editable!", "e"
        return
    end

    path = readFile("Enter full path of screenshots or type 0 to skip", true)
    return if path == "0"

    # Iterate directory and understand what type of screenshots are relevant
    filesDict = {}
    $config["misc"]["screenshotsDeviceFiles"].each do |deviceType|
        $config["misc"]["screenshotsFileExtensions"].each do |fileExt|
            localGlob = Dir.glob(path + "/" + deviceType + "-[1-#{$config["misc"]["maxScreenshots"].to_i}]" + fileExt)
            localGlob.each do |f|
                key = File.basename(f, ".*")
                filesDict[key] = f
            end
        end
    end

    puts "Found #{filesDict.length} screenshots for: #{filesDict.keys.join(", ")}"

    # Menu
    puts "Select option:\n[ 0] - Fill screenshots in empty places only (no override)\n[ 1] - Override all screenshots\n[ 2] - Select localizations to override screenshots\n[ 3] - Back"
    option = readNumber(0, 3)
    return if option == 3

    override = (option >= 1 and option <= 2)

    v = $currLogin["currApp"].edit_version
    screenshots = v.screenshots
    langs = screenshots.keys

    # Iterate all langs
    if (option >= 0 and option <= 1)
        langs.each do |lang|
            modified = false
            filesDict.each do |key|
                (deviceType,order) = key[0].split("-")
                order = order.to_i

                # Find position of device in list of ITC device types
                itcDevice = $config["misc"]["screenshotsDevices"][$config["misc"]["screenshotsDeviceFiles"].find_index(deviceType)]

                # skip if not overriding and screenshot already exists
                if not override and (screenshots[lang].find {|x| x.device_type == itcDevice and x.sort_order == order} != nil)
                    puts "Skipping language #{lang} device #{deviceType} screenshot \##{order}"
                    next
                end

                puts "Uploading screenshot to language #{lang} device #{deviceType} screenshot \##{order}"
                v.upload_screenshot!(key[1], order, lang, itcDevice)
                modified = true
            end
            if modified
                puts "Saving app info on ITC... "
                v.save!
            end
        end
    else
        puts "Available localizations:"
        i = 0
        langs.each do |lang|
            puts "[#{i.to_s.rjust(2)}] - #{lang}"
            i+=1
        end
        puts "[#{i.to_s.rjust(2)}] - Back\nEnter langs separated by commas:"
        options = gets().chomp
        return if options == i-1

        puts "Uploading screenshots to localizations: #{options.split(",").map {|l| langs[l.to_i]}}"
        options.split(",").each do |index|
            lang = langs[index.to_i]
            filesDict.each do |key|
                (deviceType,order) = key[0].split("-")
                order = order.to_i

                # Find position of device in list of ITC device types
                itcDevice = $config["misc"]["screenshotsDevices"][$config["misc"]["screenshotsDeviceFiles"].find_index(deviceType)]

                puts "Uploading screenshot to language #{lang} device #{deviceType} screenshot \##{order}"
                v.upload_screenshot!(key[1], order, lang, itcDevice)
            end
            puts "Saving app info on ITC... "
            v.save!
        end
    end
end

def createNewBuild()
    type = $currLogin["currAppType"]
    createNewDentistBuild() if type == TYPES::DENTIST
    createNewSlotsBuild() if type == TYPES::SLOTS
end

def createNewDentistBuild()
    #name
    puts "Enter game name (press enter to use \"#{$currLogin["currAppName"]}\" or enter 0 to return):"
    name = gets().chomp()
    return if name == "0"
    name = $currLogin["currAppName"] if name == ""
    $currLogin["currAppName"] = name

    #source
    source = readFile("Enter source path or 0 to return", true)
    return if source == "0"

    #target
    target = readFile("Enter target path (with duplicated prototype) or 0 to return", true)
    return if target == "0"

    #bundle ID
    puts "Enter bundle ID (press enter to use \"#{$currLogin["currBundleID"]}\" or enter 0 to return):"
    bundleID = gets().chomp()
    return if bundleID == "0"
    bundleID = $currLogin["currBundleID"] if bundleID == ""

    #IAP
    puts "Enter IAP prefix (press enter to use \"#{$currLogin["currBundleID"]}\" or enter 0 to return):"
    iap = gets().chomp()
    return if iap == "0"
    iap = $currLogin["currBundleID"] if iap == ""

    #universe ID & Flurry
    universe = ""
    flurry = ""
    while universe == "" do
        if $currIDs["universe"] != NONE
            puts "Do you want to use this Universe ID #{$currIDs["universe"]} ([y]/n, 0 to return)?"
            universe = gets().chomp()
            return if universe == "0"
            universe = $currIDs["universe"] if universe.downcase == 'y' or universe == ""
        else
            puts "Enter universe ID or just press enter to call universe script. enter 0 to return:"
            universe = gets().chomp()
            return if universe == "0"
            if universe == ""
                createUniverseID()
                universe = $currIDs["universe"]
                flurry = $currIDs["flurry"]
            end
        end
        $currIDs["universe"] = universe
    end

    while flurry == "" do
        if $currIDs["flurry"] != NONE
            puts "Do you want to use this Flurry ID #{$currIDs["flurry"]} ([y]/n, 0 to return)?"
            flurry = gets().chomp()
            return if flurry == "0"
            flurry = $currIDs["flurry"] if flurry.downcase == 'y' or flurry == ""
        else
            puts "Enter Flurry ID or just press enter to call flurry script. enter 0 to return:"
            flurry = gets().chomp()
            return if flurry == "0"
            if flurry == ""
                createFlurryID()
                flurry = $currIDs["flurry"]
            end
        end
        $currIDs["flurry"] = flurry
    end

    #Ver
    puts "Enter version (default is 1.0 or enter 0 to return):"
    ver = gets().chomp()
    return if ver == "0"
    ver = "1.0" if ver == ""

    puts "Name: #{name}\nSource:#{source}\nTarget:#{target}\nBundleID:#{bundleID}\nIAP:#{iap}\nUniverse ID:#{universe}\nFlurry App ID:#{flurry}\nVersion:#{ver}"
    puts "Are these details correct? ([y]/n)"
    option = gets().chomp()
    return createNewDentistBuild() if option.downcase == "n"

    execute($config["externalUtilities"]["dir"] + $config["externalUtilities"]["reskin dentist"] + " -name '#{name}' -source '#{source}' -target '#{target}' -bundle #{bundleID} -iap #{iap} -id #{universe} -flurry #{flurry} -ver #{ver} -run 1")
end

def createNewSlotsBuild()
    puts "Which script do you want to use? (1-reskin ios, 2-reskin gfx2ios)"
    option = readNumber(1,2)
    createNewSlotsBuildReskinIOS if option == 1
    createNewSlotsBuildReskinGFX2IOS if option == 2
end

def createNewSlotsBuildReskinIOS()
    #name
    puts "Enter game name (press enter to use \"#{$currLogin["currAppName"]}\" or enter 0 to return):"
    name = gets().chomp()
    return if name == "0"
    name = $currLogin["currAppName"] if name == ""
    $currLogin["currAppName"] = name

    #source
    source = readFile("Enter source path or 0 to return", true)
    return if source == "0"

    #target
    target = readFile("Enter target path (with duplicated prototype) or 0 to return", true)
    return if target == "0"

    #bundle ID
    puts "Enter bundle ID (press enter to use \"#{$currLogin["currBundleID"]}\" or enter 0 to return):"
    bundleID = gets().chomp()
    return if bundleID == "0"
    bundleID = $currLogin["currBundleID"] if bundleID == ""

    #IAP
    puts "Enter IAP prefix (press enter to use \"#{$currLogin["currBundleID"]}\" or enter 0 to return):"
    iap = gets().chomp()
    return if iap == "0"
    iap = $currLogin["currBundleID"] if iap == ""

    #Leaderboard
    puts "Enter leaderboard (press enter to use \"#{$currLogin["currBundleID"]}.leaderboard\" or enter 0 to return):"
    leaderboard = gets().chomp()
    return if leaderboard == "0"
    leaderboard = $currLogin["currBundleID"] + ".leaderboard" if leaderboard == ""

    #universe ID & Flurry
    universe = ""
    flurry = ""
    while universe == "" do
        if $currIDs["universe"] != NONE
            puts "Do you want to use this Universe ID #{$currIDs["universe"]} ([y]/n, 0 to return)?"
            universe = gets().chomp()
            return if universe == "0"
            universe = $currIDs["universe"] if universe.downcase == 'y' or universe == ""
        else
            puts "Enter universe ID or just press enter to call universe script. enter 0 to return:"
            universe = gets().chomp()
            return if universe == "0"
            if universe == ""
                createUniverseID()
                universe = $currIDs["universe"]
                flurry = $currIDs["flurry"]
            end
        end
        $currIDs["universe"] = universe
    end

    while flurry == "" do
        if $currIDs["flurry"] != NONE
            puts "Do you want to use this Flurry ID #{$currIDs["flurry"]} ([y]/n, 0 to return)?"
            flurry = gets().chomp()
            return if flurry == "0"
            flurry = $currIDs["flurry"] if flurry.downcase == 'y' or flurry == ""
        else
            puts "Enter Flurry ID or just press enter to call flurry script. enter 0 to return:"
            flurry = gets().chomp()
            return if flurry == "0"
            if flurry == ""
                createFlurryID()
                flurry = $currIDs["flurry"]
            end
        end
        $currIDs["flurry"] = flurry
    end

    #parse ID
    parseAppId = ""
    parseClientKey = ""
    while parseAppId == "" do
        if $currIDs["parseAppID"] != NONE
            puts "Do you want to use this Parse App ID #{$currIDs["parseAppID"]} ([y]/n, 0 to return)?"
            parseAppId = gets().chomp()
            return if parseAppId == "0"
            parseAppId = $currIDs["parseAppID"] if parseAppId.downcase == 'y' or parseAppId == ""
            parseAppId = NONE if parseAppId.downcase == "n"
        else
            puts "Enter Parse App ID or just press enter to call parse script. enter 0 to return:"
            parseAppId = gets().chomp()
            return if parseAppId == "0"
            if parseAppId == ""
                createParse()
                parseAppID = $currIDs["parseAppID"]
                parseClientKey = $currIDs["parseClientKey"]
            end
        end
        $currIDs["parseAppID"] = parseAppId
    end

    while parseClientKey == "" do
        if $currIDs["parseClientKey"] != NONE
            puts "Do you want to use this Parse Client Key #{$currIDs["parseClientKey"]} ([y]/n, 0 to return)?"
            parseClientKey = gets().chomp()
            return if parseClientKey == "0"
            parseClientKey = $currIDs["parseClientKey"] if parseClientKey.downcase == 'y' or parseClientKey == ""
            parseClientKey = NONE if parseClientKey.downcase == "n"
        else
            puts "Enter Parse Client Key, enter 0 to return:"
            parseClientKey = gets().chomp()
            return if parseClientKey == "0"
        end
        $currIDs["parseClientKey"] = parseClientKey
    end

    #Coins
    puts "Enter coins (500-1000000, default is 5000 or enter 0 to return):"
    coins = readNumber(0,1000000, true)
    return if coins == "0"
    coins = 5000 if coins == ""
    coins = 500 if coins <= 500

    #Ver
    puts "Enter version (default is 1.0 or enter 0 to return):"
    ver = gets().chomp()
    return if ver == "0"
    ver = "1.0" if ver == ""

    puts "Name: #{name}\nSource:#{source}\nTarget:#{target}\nBundleID:#{bundleID}\nIAP:#{iap}\nLeaderboard:#{leaderboard}\nUniverse ID:#{universe}\nFlurry App ID:#{flurry}\nParse App ID:#{parseAppId}\nParse Client Key:#{parseClientKey}\nCoins:#{coins}\nVersion:#{ver}"
    puts "Are these details correct? ([y]/n)"
    option = gets().chomp()
    return createNewSlotsBuildReskinIOS() if option.downcase == "n"

    execute($config["externalUtilities"]["dir"] + $config["externalUtilities"]["reskin ios"] + " -name '#{name}' -source '#{source}' -target '#{target}' -bundle #{bundleID} -iap #{iap} -leaderboard #{leaderboard} -id #{universe} -flurry #{flurry} -parseid #{parseAppId} -parseck #{parseClientKey} -coins #{coins} -ver #{ver} -run 1")
end

def createNewSlotsBuildReskinGFX2IOS()
    #name
    puts "Enter game name (press enter to use \"#{$currLogin["currAppName"]}\" or enter 0 to return):"
    name = gets().chomp()
    return if name == "0"
    name = $currLogin["currAppName"] if name == ""
    $currLogin["currAppName"] = name

    #source
    assets = readFile("Enter assets path or 0 to return", true)
    return if assets == "0"

    #source
    icons = readFile("Enter icons path or 0 to return", true)
    return if icons == "0"

    #target
    target = readFile("Enter target path (with duplicated prototype) or 0 to return", true)
    return if target == "0"

    #bundle ID
    puts "Enter bundle ID (press enter to use \"#{$currLogin["currBundleID"]}\" or enter 0 to return):"
    bundleID = gets().chomp()
    return if bundleID == "0"
    bundleID = $currLogin["currBundleID"] if bundleID == ""

    #IAP
    puts "Enter IAP prefix (press enter to use \"#{$currLogin["currBundleID"]}\" or enter 0 to return):"
    iap = gets().chomp()
    return if iap == "0"
    iap = $currLogin["currBundleID"] if iap == ""

    #Leaderboard
    puts "Enter leaderboard (press enter to use \"#{$currLogin["currBundleID"]}.leaderboard\" or enter 0 to return):"
    leaderboard = gets().chomp()
    return if leaderboard == "0"
    leaderboard = $currLogin["currBundleID"] + ".leaderboard" if leaderboard == ""

    #universe ID
    universe = ""
    flurry = ""
    while universe == "" do
        if $currIDs["universe"] != NONE
            puts "Do you want to use this Universe ID #{$currIDs["universe"]} ([y]/n, 0 to return)?"
            universe = gets().chomp()
            return if universe == "0"
            universe = $currIDs["universe"] if universe.downcase == 'y' or universe == ""
        else
            puts "Enter universe ID or just press enter to call universe script. enter 0 to return:"
            universe = gets().chomp()
            return if universe == "0"
            if universe == ""
                createUniverseID()
                universe = $currIDs["universe"]
                flurry = $currIDs["flurry"]
            end
        end
        $currIDs["universe"] = universe
    end

    while flurry == "" do
        if $currIDs["flurry"] != NONE
            puts "Do you want to use this Flurry ID #{$currIDs["flurry"]} ([y]/n, 0 to return)?"
            flurry = gets().chomp()
            return if flurry == "0"
            flurry = $currIDs["flurry"] if flurry.downcase == 'y' or flurry == ""
        else
            puts "Enter Flurry ID or just press enter to call flurry script. enter 0 to return:"
            flurry = gets().chomp()
            return if flurry == "0"
            if flurry == ""
                createFlurryID()
                flurry = $currIDs["flurry"]
            end
        end
        $currIDs["flurry"] = flurry
    end

    #parse ID
    parseAppId = ""
    parseClientKey = ""
    while parseAppId == "" do
        if $currIDs["parseAppID"] != NONE
            puts "Do you want to use this Parse App ID #{$currIDs["parseAppID"]} ([y]/n, 0 to return)?"
            parseAppId = gets().chomp()
            return if parseAppId == "0"
            parseAppId = $currIDs["parseAppID"] if parseAppId.downcase == 'y' or parseAppId == ""
            parseAppId = NONE if parseAppId.downcase == "n"
        else
            puts "Enter Parse App ID or just press enter to call parse script. enter 0 to return:"
            parseAppId = gets().chomp()
            return if parseAppId == "0"
            if parseAppId == ""
                createParse()
                parseClientKey = $currIDs["parseClientKey"]
            end
        end
        $currIDs["parseAppID"] = parseAppId
    end

    while parseClientKey == "" do
        if $currIDs["parseClientKey"] != NONE
            puts "Do you want to use this Parse Client Key #{$currIDs["parseClientKey"]} ([y]/n, 0 to return)?"
            parseClientKey = gets().chomp()
            return if parseClientKey == "0"
            parseClientKey = $currIDs["parseClientKey"] if parseClientKey.downcase == 'y' or parseClientKey == ""
            parseClientKey = NONE if parseClientKey.downcase == "n"
        else
            puts "Enter Parse Client Key, enter 0 to return:"
            parseClientKey = gets().chomp()
            return if parseClientKey == "0"
        end
        $currIDs["parseClientKey"] = parseClientKey
    end

    #Coins
    puts "Enter coins (500-1000000, default is 5000 or enter 0 to return):"
    coins = readNumber(0,1000000, true)
    return if coins == "0"
    coins = 5000 if coins == ""
    coins = 500 if coins <= 500

    #Ver
    puts "Enter version (default is 1.0 or enter 0 to return):"
    ver = gets().chomp()
    return if ver == "0"
    ver = "1.0" if ver == ""

    puts "Name: #{name}\nAssets:#{assets}\nIcons:#{icons}\nTarget:#{target}\nBundleID:#{bundleID}\nIAP:#{iap}\nLeaderboard:#{leaderboard}\nUniverse ID:#{universe}\nFlurry App ID:#{flurry}\nParse App ID:#{parseAppId}\nParse Client Key:#{parseClientKey}\nCoins:#{coins}\nVersion:#{ver}"
    puts "Are these details correct? ([y]/n)"
    option = gets().chomp()
    return createNewSlotsBuildReskinIOS() if option.downcase == "n"

    execute($config["externalUtilities"]["dir"] + $config["externalUtilities"]["reskin gfx2ios"] + " -name '#{name}' -assets '#{assets}' -icons '#{icons}' -target '#{target}' -bundle #{bundleID} -iap #{iap} -leaderboard #{leaderboard} -id #{universe} -flurry #{flurry} -parseid #{parseAppId} -parseck #{parseClientKey} -coins #{coins} -ver #{ver} -run 1")
end

def createPushNotification()
    puts "Creating Push Notification certificate for #{$currLogin["currBundleID"]} for user #{$currLogin["currAccount"]} using pem (make sure you have it installed)..."
    system("pem -a #{$currLogin["currBundleID"]} -u #{$currLogin["currAccount"]}")
end

def createProvisioningFile()
    puts "Checking if provisioning file already exists..."
    filename = "#{$currLogin["currAppName"]}.mobileprovision"

    prov = Spaceship.provisioning_profile.app_store.find_by_bundle_id($currLogin["currBundleID"])
    if prov.empty?
        puts "Couldn't find provisioning file on Portal, creating one..."
        cert = Spaceship.certificate.production.find($config["productionCertID"][$currLogin["currAccount"]])
        prov = Spaceship.provisioning_profile.app_store.create!(bundle_id: $currLogin["currBundleID"], name: "#{$currLogin["currAppName"]} - Prod", certificate: cert)
    else
        puts "Found provisioning file."
        prov = prov[0]
    end

    puts "Downloading to #{filename}..."
    File.write(filename, prov.download)
    puts "Done."
end

def createFlurryID()
    type = $currLogin["currAppType"].downcase
    puts "Game type is #{type}"
    puts "Enter game name (press enter to use \"#{$currLogin["currAppName"]}\" or enter 0 to return):"
    name = gets().chomp()
    return if name == "0"
    name = $currLogin["currAppName"] if name == ""
    $currLogin["currAppName"] = name

    returnValue = execute($config["externalUtilities"]["dir"] + $config["externalUtilities"]["flurry"] + " -name '#{name}' -type #{type} -platform ios")
    $currIDs["flurry"] = returnValue.split("acc respond:")[1]
    puts "Flurry ID: #{$currIDs["flurry"]}"
end

def createUniverseID()
    puts "Enter game name (press enter to use \"#{$currLogin["currAppName"]}\" or enter 0 to return):"
    name = gets().chomp()
    return if name == "0"
    name = $currLogin["currAppName"] if name == ""
    $currLogin["currAppName"] = name

    flurry = ""
    while flurry == "" do
        if $currIDs["flurry"] != NONE
            puts "Do you want to use this Flurry ID #{$currIDs["flurry"]} ([y]/n, 0 to return)?"
            flurry = gets().chomp()
            return if flurry == "0"
            flurry = $currIDs["flurry"] if flurry.downcase == 'y' or flurry == ""
        else
            puts "Enter flurry ID or just press enter to call flurry script. enter 0 to return:"
            flurry = gets().chomp()
            return if flurry == "0"
            if flurry == ""
                createFlurryID()
                flurry = $currIDs["flurry"]
            end
        end
    end
    $currIDs["flurry"] = flurry

    template = ($currLogin["currAppType"] == TYPES::DENTIST ? 'dentist' : 'slots v3')

    returnValue = execute($config["externalUtilities"]["dir"] + $config["externalUtilities"]["universe"] + " -name '#{name}' -flurry #{flurry} -template '#{template}'")
    $currIDs["universe"] = returnValue.split("acc respond:")[1]
    puts "Universe ID: #{$currIDs["universe"]}"
end

def createParse()
    puts "Enter game name (press enter to use \"#{$currLogin["currAppName"]}\" or enter 0 to return):"
    name = gets().chomp()
    return if name == "0"
    name = $currLogin["currAppName"] if name == ""
    $currLogin["currAppName"] = name

    returnValue = execute($config["externalUtilities"]["dir"] + $config["externalUtilities"]["parse"] + " -name '#{name}' -account #{$currLogin["currAccount"]}")
    ($currIDs["parseAppID"], $currIDs["parseClientKey"]) = returnValue.split("acc respond:")[1].split(",")
    puts "Parse App ID: #{$currIDs["parseAppID"]}\nParse Client Key: #{$currIDs["parseClientKey"]}"
end

def selectLatestBuild()
    if not appIsEditable($currLogin["currApp"])
        putsc "App is not editable!", "e"
        return
    end

    v = $currLogin["currApp"].edit_version
    builds = v.candidate_builds
    builds.each {|b| buildsStatus+="#{b.build_version} (#{b.train_version}) " + (b.processing ? "Processing... |" : " Ready to use! |")}
    puts (buildsStatus == "" ? "No builds" : buildsStatus[0..-3])

    if defined? builds[0].processing and !builds[0].processing
        v.select_build(builds[0])
        status += " #{builds[0].build_version} was selected."
        v.save!
    else
        puts "Latest build is not processed yet..."
    end
end

def submitForReview()
    puts "Not yet implemented..."
end

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Appstore utilities

# app is editable
def appIsEditable(app)
    begin
        return (not app.edit_version.nil?)
    rescue Spaceship::Client::UnexpectedResponse
        putsc "Connection lost...", "e"
        setCurrentApp(NONE, NONE, NONE, NONE)
    end
end

def appStatus(app)
    begin
        return (appIsEditable(app) ? ((not app.live_version.nil?) ? APPSTATUS::LIVE_EDITABLE : APPSTATUS::EDITABLE ) : ((not app.live_version.nil?) ? APPSTATUS::LIVE : APPSTATUS::NOT_EXIST ))
    rescue Spaceship::Client::UnexpectedResponse
        putsc "Connection lost...", "e"
        setCurrentApp(NONE, NONE, NONE, NONE)
    end
end

def appUpdatePriceTier(app="", tier="")
    app = $currLogin["currApp"] if app == ""
    tier = $config["new#{$currLogin["currAppType"]}"]["priceTier"] if tier == ""

    puts "Updating tier..."
    app.update_price_tier!(tier)
end

def appUpdateCatergories(app="", config="")
    app = $currLogin["currApp"] if app == ""
    config = $config["new#{$currLogin["currAppType"]}"] if config == ""

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
puts "Appstore Control Center V1.13 - By Liran Cohen"
init()
pageBreak()
mainMenu()

# first keywords, then upload screenshots then titles