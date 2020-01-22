var request = require('request');

const options = {
    method: 'GET',
    url: 'http://api.bitbucket.org/2.0/repositories/kevcai/test-repo/refs/branches',
    headers: {
    }
}

request(options, function (error, response) { 
    if (error) throw new Error(error);
    var body = JSON.parse(response.body);
    console.log(body)
    console.log("____________");
    console.log(body.values);
})