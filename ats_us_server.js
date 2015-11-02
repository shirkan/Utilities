var locallydb = require('locallydb');
var mandrill = require('mandrill-api/mandrill');
var express = require('express');
var fs = require('fs');
var request = require('request');
var cheerio = require('cheerio');
var http = require('http');
var app     = express();

//  Globals
var num_of_games = 200;
var mandrill_client = new mandrill.Mandrill('78MeL8wSNNw6CkhRDnQzlw');
var db = new locallydb('./games_db');
var collection = db.collection('new_us');
const collectionEmpty = { items: [] };

//  Output globals
var output = [];
var output_line = 0;

//  Step 1: filter all games on USA
var countries_code = {  usa: 'us'}

var tables = {};
var ranks = {};
var ids_to_names = [];
var countries_completed = 0;

var categories = ["topfreeapplications", "topfreeipadapplications", "toppaidapplications", "toppaidipadapplications"];
var categoriesToNames = {
    topfreeapplications: "iPhone Free", 
    topfreeipadapplications: "iPad Free", 
    toppaidapplications: "iPhone Paid", 
    toppaidipadapplications: "iPad Paid"
};
var categories_iterator = 0;

// Step 2: check if games are really not in USA (maybe has lower rank than 200)
var ids_to_check_count = 0;

//  Date consts.
const ParInDays = 10;
const ParTime = 1000 * 60 * 60 * 24 * ParInDays;
const Now = new Date();

function sendMail(data) { 
	var message = {
	    "text": "New game(s) alert:\n" + data,
	    "subject": "[ATS] USA New Game(s) Alert",
	    "from_email": "automator@totemedia.co",
	    "from_name": "[ATS] by Liran Cohen",
	    "to": [{
	            "email": "tridentcanadainc@gmail.com",
	            "name": "Trident inc.",
	            "type": "to"
	        }]
	};
	var async = false;
	mandrill_client.messages.send({"message": message, "async": async}, function(result) {
	    console.log(result);
	}, function(e) {
	    // Mandrill returns the error as an object with name and message keys
	    console.log('A mandrill error occurred: ' + e.name + ' - ' + e.message);
	    // A mandrill error occurred: Unknown_Subaccount - No subaccount exists with the id 'customer-123'
	});
}

function getURLforCountry (country, category) {
    var str = 'http://www.appninjaz.com/appsense/index.php?chart=' + category +'&country=' + countries_code[country] + '&genre=6014'; 
    return str;
}

function checkIfScriptIsDone() {
    ids_to_check_count--;
    if (!ids_to_check_count) {
        //  No more ids to check. move to next category.
        categories_iterator++;
        iterateNextCategory();
    }
}

function getGameReleaseDateInCountry(country, id) {
    var options = {
      host: 'itunes.apple.com',
      path: '/lookup?id=' + id + '&country=' + countries_code[country]
    };

    callback = function(response) {
      var str = '';

      //another chunk of data has been recieved, so append it to `str`
      response.on('data', function (chunk) {
        str += chunk;
      });

      //the whole response has been recieved, so we just print it out here
      response.on('end', function () {
        str = JSON.parse(str);
        
        var rawDate = str["results"][0]["releaseDate"].split("T")[0].split("-");
        var GameDateObject = new Date(rawDate);
        // GameDateObject.setMonth(GameDateObject.getMonth() - 1);
        // console.log("calc: " + (Now - ParTime) + " <  " + GameDateObject + " = " + (Now - ParTime < GameDateObject));

        //  Only report game if he's one week old maximum
        if (Now - ParTime < GameDateObject) {
            var date = ("0" + rawDate[2]).slice(-2) + "/" + ("0" + rawDate[1]).slice(-2) + "/" + rawDate[0];
            var date_reversed = rawDate[0] + "/" + ("0" + rawDate[1]).slice(-2) + "/" + ("0" + rawDate[2]).slice(-2);
            
            entry = date_reversed + " - New in USA: [Rank #" + ranks[country][id] + "]: " + id + " - " + ids_to_names[id] + " - " + date + " - " + categoriesToNames[categories[categories_iterator]] + 
                ' - http://www.appninjaz.com/appsense/app_details.php?app_id=' + id + '&country=' + countries_code[country];
            output.push(entry);
        }
        
        checkIfScriptIsDone();

      });
    }

    http.request(options, callback).end();
}

function get_games_list ( country , category) {
    console.log('Looking for ' + country);
    var url = getURLforCountry(country, category);
    if (!url) {
        console.log("no url for " + country);
        return;
    }
    console.log("Found " + country + " with url: " + url);
    request(url, function(error, response, html){
        
        //  Check if we found at least one new ID
        atLeastOneID = false;

        if(!error){
            var $ = cheerio.load(html);
            
            // skip children 0 because it's titles row
            tables[country] = [];
            ranks[country] = [];
            for (var i = 1; i<=num_of_games; i++) {
                var id = $("#game_name_" + i)[0]["attribs"]["href"].split("=")[1].split("&")[0];
                var idInStorage = country + "_" + id;
                
                // Check if game was already reported
                if (collection.where({id : idInStorage}).items.length) {
                	continue;
                } else {

                    //  Get game details
                    var name = $("#game_name_" + i).text();
                    ids_to_names[id] = name;
                    ids_to_check_count++;
                    tables[country].push(id);
                    ranks[country][id] = i;

                    //  Update DB that we handled this ID
                    collection.insert({id : idInStorage});
                    collection.save();
                    atLeastOneID = true;
                }

            }
        } else {
            console.log(error);
        }

        console.log('Done loading list for ' + country + ". Pushed " + tables[country].length + " IDs. (" + countries_completed + "/" + Object.keys(countries_code).length + ")");

        if (ids_to_check_count) {
            console.log('Getting games info...');
            for (var i in tables[country]) {
                if (i % 1 !== 0) {
                    continue;
                }
                var game_id = (tables[country])[i];
                getGameReleaseDateInCountry(country, game_id);
            }
        } else {
            console.log("No new IDs to check...")
            categories_iterator++;
            iterateNextCategory();
        }
    });  
}

function iterateNextCategory () {
    if (categories_iterator < categories.length) {
        currentCategory = categories[categories_iterator];
        console.log("Checking " + currentCategory + " (" + (categories_iterator+1) + "/" + categories.length + ")");
        countries_completed = 0;
        ids_to_check_count = 0;
        for (var country in countries_code) {
            get_games_list(country, currentCategory);    
        }
    } else {
        if (output.length) {
            sendMail(output.sort().reverse().join("\n\n"));    
        }
        console.log("Done comparison.");
    }
}

console.log('Running american trends script. Time: ' + new Date().toJSON().replace(/T/," "));
iterateNextCategory();

exports = module.exports = app;