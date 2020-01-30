// Git Automation Script
// Written by Kevin Cai, Jan 2020

var request = require('request');
const https = require('https');

// PARAMS: email_id, production_release, release_branch, target_env
// node git-update.js target_repo release_branch target_env
var myArgs = process.argv.slice(2)

var release_branch = myArgs[0]

// get all repositories
// /repositories/{workspace} - returns all repos under the specified UUID


//for all repositories

    //branch logic

// email list

function request_repo() {
    return new Promise(function(resolve, reject) {
        request('https://api.bitbucket.org/2.0/repositories/kevcai', function(error, response, body) {
            if (error) return reject(error)
            resolve(body)
        })
    })
}

// find release_branch
function find_repo(repos) {
    repos.values.forEach(element => {
        //console.log(element)
        console.log('------------')
        console.log(element.slug)
        if (element.slug == release_branch) {
            console.log("FOUND")
            return element.link.branch
        }
    });
}


async function main() {
    try{
        var res = await request_repo();
        repos = await JSON.parse(res)
        find_repo(repos)

    } catch (error) {
        console.error(error)
    }

    
}
main()