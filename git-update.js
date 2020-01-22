// Git Automation Script
// Written by Kevin Cai, Jan 2020

var request = require('request');
const https = require('https');


// PARAMS: email_id, production_release, release_branch, target_env


// get all repositories
// /repositories/{workspace} - returns all repos under the specified UUID
var repos = get_repos()

//for all repositories

    //branch logic

// email list
function get_repos() {
    https.get('https://api.bitbucket.org/2.0/repositories/kevcai', (resp) => {
        let data = ''

        resp.on('data', (chunk) => {
            data += chunk
        })

        resp.on('end', () => {
            var ret = JSON.parse(data).values
            console.log(ret)
            return ret
        })
    }).on('error', (err) => {
        console.log("Error: " + err.message)
    })
}

/*
function get_repos() {
    const options = {
        method: 'GET',
        url: 'https://api.bitbucket.org/2.0/repositories/kevcai', //    /2.0/repositories/{workspace}
        headers: {
        }
    }

    request(options, function (error, response) { 
        if (error) throw new Error(error)
        var body = JSON.parse(response.body)
        console.log(body)
        console.log("____________")
        console.log(body.values)
        return body.values
    })
*/