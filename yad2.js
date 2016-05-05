var express = require('express');
var fs = require('fs');
var request = require('request');
var cheerio = require('cheerio');
var app     = express();

app.get('/scrape', function(req, res){
    url = 'http://my.yad2.co.il/MyYad2/MyOrder/Yad2.php';

    request(url, function(error, response, html){

        // First we'll check to make sure no errors occurred when making the request

        if(!error){
            // Next, we'll utilize the cheerio library on the returned html which will essentially give us jQuery functionality

            var $ = cheerio.load(html);

            // Finally, we'll define the variables we're going to capture

            var title, release, rating;
            var json = { title : "", release : "", rating : ""};
        }
    })
})

app.listen('8081')
console.log('Magic happens on port 8081');
exports = module.exports = app;



mainUrl = 'http://my.yad2.co.il/MyYad2/MyOrder/Yad2.php';
loginUrl = "http://my.yad2.co.il/login.php";
request.post(loginUrl, function (error, response, body) {
  if (!error && response.statusCode == 200) {
    request.get(mainUrl, function (error2, response2, body2) {
        console.log(body2) // Show the HTML for the Google homepage.
    })
  }
})