# Git Automation Script
# Written by Kevin Cai, Jan 2020

# Usage: python3.8 git-update.py <target_repo> <production_branch> <release_branch>
import requests
import sys
from pprint import pprint
import json
from base64 import b64encode

# /repositories/{workspace} - returns all repos under the specified UUID
REPO_URL = 'https://api.bitbucket.org/2.0/repositories/kevcai' # corresponds to specific workspace (will be DPE icare workspace url) -> search all repos under that workspace
AUTH_TOKEN =  'Basic {}'.format(b64encode(b"kevcai@deloitte.com.au:f4ithGa1ns").decode("ascii")) # basic auth generated using bitbucket user credentials - necessary to access private repos
PROJECT_RELEASE = 'master' # master should be the same as project release

# basic get request function
def get_request(url):
    URL = url
    PARAMS = {}
    HEADERS = {
        'Authorization': AUTH_TOKEN
    }
    r = requests.get(url=URL, params=PARAMS, headers=HEADERS)
    return r.json()

# helper function to find specific repo in a repo_list json
def find_repo(repo_list, repo):
    for r in repo_list:
        if (r['slug'] == repo):
            return r
    return None

# makes a POST request to BitBucket API - requests a pull request
def make_pull_request(pull_url, source_branch, dest_branch):
    print("Attempting to make pull request from <{}> to <{}>".format(source_branch, dest_branch))
    url = pull_url

    body = {
        'title': '{}'.format(gen_pull_title(source_branch, dest_branch)),
        'source': {
            'branch': {
                'name': '{}'.format(source_branch)
            }
        },
        'destination': {
            'branch': {
                'name': '{}'.format(dest_branch)
            }
        }
    }
    payload = json.dumps(body)
    headers = {     
    'Content-Type': 'application/json',
    'Authorization': AUTH_TOKEN       
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    return response

# helper function to generate string to serve as pull request title
def gen_pull_title(source_branch, dest_branch):
    return "Merge {} into {}".format(source_branch, dest_branch)


# main scripting logic
def main(target_repo, production_branch, release_branch):
    res = get_request(REPO_URL)
    repo_link = find_repo(res['values'], target_repo)       # get repo info for the target repo

    if (repo_link == None):
        sys.exit('Target Repo <{}> Not Found'.format(target_repo))

    pull_url = repo_link['links']['pullrequests']['href']

    pull_res = make_pull_request(pull_url, PROJECT_RELEASE, production_branch)       

    # if pull request is not successful:
    if (pull_res.status_code == 400):       # return relevant message for pull request failure (no changes, branch not exist, etc.)
        data = pull_res.json()
        message = data['error']['message']
        sys.exit(message)
        
    if (pull_res.status_code == 201):
        sys.exit('Pull request successfully created.')

if __name__ == "__main__":
    if (len(sys.argv) < 4):
        sys.exit('Usage: python3 git-update.py <target_repo> <production_branch> <release_branch>')

    target_repo = sys.argv[1]
    production_branch = sys.argv[2]
    release_branch = sys.argv[3]

    main(target_repo, production_branch, release_branch)
