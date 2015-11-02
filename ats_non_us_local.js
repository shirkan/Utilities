var express = require('express');
var fs = require('fs');
var request = require('request');
var cheerio = require('cheerio');
var http = require('http');
var app     = express();

//  Globals
var num_of_games = 200;

//  Output globals
var output = [];
var output_line = 0;

//  Step 1: filter all games which are on CA / AUS and not on USA
var countries_code = {  canada : 'ca',
                        usa: 'us',
                        australia: 'au',
                        uk : 'uk'}
                        // israel: 'il',
                        // france: 'fr'};

var categories = ["topfreeapplications", "topfreeipadapplications", "toppaidapplications", "toppaidipadapplications"];
var categories_iterator = 0;

// var urls = {    canada : 'http://www.appninjaz.com/appsense/index.php?chart=topfreeapplications&country=ca&genre=6014',
//                 usa: 'http://www.appninjaz.com/appsense/index.php?chart=topfreeapplications&country=us&genre=6014',
//                 australia: 'http://www.appninjaz.com/appsense/index.php?chart=topfreeapplications&country=au&genre=6014'}
//                 // israel: 'http://www.appninjaz.com/appsense/index.php?chart=topfreeapplications&country=il&genre=6014'};

var tables = {};
var ranks = {};
var ids_to_names = [];
var countries_completed = 0;

// Step 2: check if games are really not in USA (maybe has lower rank than 200)
var ids_to_check = {};
var ids_to_check_count = 0;

//  Date consts.
const ParInDays = 10;
const ParTime = 1000 * 60 * 60 * 24 * ParInDays;
const Now = new Date();

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
        // console.log("rawDate: " + rawDate + " calc: " + (Now - ParTime) + " <  " + GameDateObject + " = " + ((Now - ParTime) < GameDateObject));

        //  Only report game if he's one week old maximum
        if ((Now - ParTime) < GameDateObject) {
            var date = ("0" + rawDate[2]).slice(-2) + "/" + ("0" + rawDate[1]).slice(-2) + "/" + rawDate[0];
            var date_reversed = rawDate[0] + "/" + ("0" + rawDate[1]).slice(-2) + "/" + ("0" + rawDate[2]).slice(-2);
            
            entry = date_reversed + " - In " + country + " but not in USA: [Rank #" + ranks[country][id] + "]: " + id + " - " + ids_to_names[id] + " - " + date + " - " + categories[categories_iterator] + "\n";
            output.push(entry);
        }
        
        checkIfScriptIsDone();

      });
    }

    http.request(options, callback).end();
}

function checkIfGameIsInUSA(country, id) {
    var options = {
      host: 'itunes.apple.com',
      path: '/lookup?id=' + id + '&country=us'
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

        if (str["resultCount"] == 0) {
            //  Game is not on USA
            getGameReleaseDateInCountry(country, id);
        } else {
            checkIfScriptIsDone();
        }

      });
    }

    http.request(options, callback).end();
}

function compareAllToUSA() {
    console.log("Comparing all countries to USA");
    var usa = tables["usa"];
    

    for (var country in tables) {
        if (country == "usa") {
            continue;
        }

        ids_to_check[country] = [];

        for (var id in tables[country]) {
            var game_id = (tables[country])[id];

            if (usa.indexOf(game_id) == -1 ) {
                ids_to_check[country].push(game_id);
                ids_to_check_count++;
            }
        }
    }

    //  Submit ids to check
    for (var country in ids_to_check) {
        console.log("Verifying " + ids_to_check[country].length + " ids in " + country + "...");
        for (var id in ids_to_check[country]) {
            checkIfGameIsInUSA(country, ids_to_check[country][id]);
        }
    }

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
        if(!error){
            var $ = cheerio.load(html);
            
            // skip children 0 because it's titles row
            tables[country] = [];
            ranks[country] = [];
            
            for (var i = 1; i<=num_of_games; i++) {
                var id = $("#game_name_" + i)[0]["attribs"]["href"].split("=")[1].split("&")[0];
                var name = $("#game_name_" + i).text();
                ids_to_names[id] = name;
                tables[country].push(id);
                ranks[country][id] = i;
            }
        } else {
            console.log(error);
        }

        // // To write to the system we will use the built in 'fs' library.
        // // In this example we will pass 3 parameters to the writeFile function
        // // Parameter 1 :  output.json - this is what the created filename will be called
        // // Parameter 2 :  JSON.stringify(json, null, 4) - the data to write, here we do an extra step by calling JSON.stringify to make our JSON easier to read
        // // Parameter 3 :  callback function - a callback function to let us know the status of our function

        filename = 'trends_' + country + '_' + categories[categories_iterator] + '.json';
        fs.writeFile(filename, JSON.stringify(tables[country], null, 4), function(err){
            console.log(country + ' -> File successfully written! - Check your project directory for the ' + filename + ' file');
        });

        countries_completed++;
        console.log('Done loading list for ' + country + " (" + countries_completed + "/" + Object.keys(countries_code).length + ")");

        if (countries_completed == Object.keys(countries_code).length) {
            // for (var key in ids_to_names) {
            //     console.log(key + " - " + ids_to_names[key])
            // }
            
            compareAllToUSA();
        }

    });  
}

function iterateNextCategory () {
    if (categories_iterator < categories.length) {
        currentCategory = categories[categories_iterator];
        console.log("Checking " + currentCategory + " (" + (categories_iterator+1) + "/" + categories.length + ")");
        countries_completed = 0;
        for (var country in countries_code) {
            get_games_list(country, currentCategory);    
        }
    } else {
        fs.writeFile('trends_output.json', output.sort().reverse(), function(err){
            console.log('File successfully written! - Check your project directory for the trends_output.json file');
        });
        console.log("Done comparison.");
    }
}

console.log('Running trends script...');
iterateNextCategory();

exports = module.exports = app;