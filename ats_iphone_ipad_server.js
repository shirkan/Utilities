var locallydb = require('locallydb');
var express = require('express');
var fs = require('fs');
var request = require('request');
var cheerio = require('cheerio');
var http = require('http');
var app     = express();
var Slack = require('slack-node');
var slackApiToken = "xoxp-18842002498-18838929923-36817106343-0d0e31f450";

//  Globals
var num_of_games = 200;
var db = new locallydb('./games_db');
var collection = db.collection('iphone_ipad');
const collectionEmpty = { items: [] };

//  Output globals
var output = [];
var output_line = 0;

//  Step 1: get all games from both iphone and ipad
var types = {   iPhone : 'http://www.appninjaz.com/appsense/index.php?chart=topfreeapplications&country=us&genre=7006',
                iPad: 'http://www.appninjaz.com/appsense/index.php?chart=topfreeipadapplications&country=us&genre=7006' }
var singles_lists = {};

var ids_to_names = [];
var types_completed = 0;

// Step 2: check if games are really not in USA (maybe has lower rank than 200)
var ids_to_check = {};
var ids_to_check_count = 0;

function sendMessage(data) {
    var message = "[ATS] iPhone Vs. iPad New Game(s) Alert:\n" + data
    var old_message = {
        "text": "New game(s) alert:\n" + data,
        "subject": "[ATS] iPhone Vs. iPad New Game(s) Alert",
        "from_email": "automator@totemedia.co",
        "from_name": "[ATS] by Liran Cohen",
        "to": [{
                "email": "tridentcanadainc@gmail.com",
                "name": "Trident inc.",
                "type": "to"
            }]
    };
    var slack = new Slack(slackApiToken);

    slack.api('chat.postMessage', {
      text:message,
      channel:'#new_trends'
    }, function(err, response){
      console.log('response: ' + response);
      console.log('err: ' + err);
    });
}

function checkIfScriptIsDone() {
    ids_to_check_count--;
    if (!ids_to_check_count) {
        //  No more ids to check. write to file and exit.

        fs.writeFile('iphone_ipad_output.csv', output, function(err){
            console.log('File successfully written! - Check your project directory for the iphone_ipad_output.csv file');
        });
        console.log("Done comparison.");
    }
}

function getGameInfo(id, kind) {
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

        var rawDate = str["results"][0]["releaseDate"].split("T")[0].split("-");
        var date = ("0" + rawDate[1]).slice(-2) + "/" + ("0" + rawDate[2]).slice(-2) + "/" + rawDate[0];

        output[output_line++] = kind + " only," + id + "," + ids_to_names[id] + "," + str["results"][0]["artistName"].replace(/,/g," ") + "," + date + "\n";
        checkIfScriptIsDone();

      });
    }

    http.request(options, callback).end();
}

function checkIfGameHasKind(id, kind) {
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

        // console.log(id + "            " +str)

        if (str["results"][0]["supportedDevices"].indexOf(kind) == -1) {
            //  Game is not of kind 'kind'
            getGameInfo(id, kind);
        } else {
            checkIfScriptIsDone();
        }

      });
    }

    http.request(options, callback).end();
}

function findSingles() {
    var iphone = singles_lists["iPhone"];
    var ipad = singles_lists["iPad"];

    output[output_line++] = ",Type, ID, Name, Company, Release date\n";

    ids_to_check["iPhone"] = [];
    for (var id in iphone) {
        var game_id = iphone[id];
        if (ipad.indexOf(game_id) == -1 ) {
            ids_to_check_count++;
            ids_to_check["iPhone"].push(game_id);
        }
    }

    ids_to_check["iPad"] = [];
    for (var id in ipad) {
        var game_id = ipad[id];
        if (iphone.indexOf(game_id) == -1 ) {
            ids_to_check_count++;
            ids_to_check["iPad"].push(game_id);
        }
    }

    console.log("Checking candidates...");

    for (var id in ids_to_check["iPhone"]) {
        checkIfGameHasKind(ids_to_check["iPhone"][id], "iPad");
    }

    for (var id in ids_to_check["iPad"]) {
        checkIfGameHasKind(ids_to_check["iPad"][id], "iPhone");
    }
}

function getGamesList ( type ) {
    var url = types[type];
    request(url, function(error, response, html){
        if(!error){
            var $ = cheerio.load(html);

            // skip children 0 because it's titles row
            singles_lists[type] = [];
            for (var i = 1; i<=num_of_games; i++) {
                var id = $("#game_name_" + i)[0]["attribs"]["href"].split("=")[1];
                var name = $("#game_name_" + i).text().replace(/,/g," ");
                ids_to_names[id] = name;
                singles_lists[type].push(id);
            }
        } else {
            console.log(error);
        }

        types_completed++;
        console.log('Done loading list for ' + type + " (" + types_completed + "/" + Object.keys(types).length + ")");

        if (types_completed == Object.keys(types).length) {
            findSingles();
        }

    });
}

console.log('Running iPhone vs. iPad script...');
for (var type in types) {
    getGamesList(type);
}

exports = module.exports = app;