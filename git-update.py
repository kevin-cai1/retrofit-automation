# Git Automation Script
# Written by Kevin Cai, Jan 2020

# Usage: python3.8 git-update.py <target_repo> <production_branch> <release_branch>
import requests
import sys
from pprint import pprint
import json
from base64 import b64encode
from datetime import datetime
import os

# /repositories/{workspace} - returns all repos under the specified UUID
REPO_URL = 'https://api.bitbucket.org/2.0/repositories/icarensw' # corresponds to specific workspace (will be DPE icare workspace url) -> search all repos under that workspace
username = os.environ.get('BITBUCKET_USERNAME')
password = os.environ.get('BITBUCKET_PASSWORD')
auth_string = "{}:{}".format(username, password)
auth_byte = bytes(auth_string, encoding="utf-8")
AUTH_TOKEN =  'Basic {}'.format(b64encode(auth_byte).decode("ascii")) # basic auth generated using bitbucket user credentials - necessary to access private repos
PROJECT_RELEASE = 'master' # master should be the same as project release

BAMBOO_HOST = 'http://localhost'    # host for Bamboo Application
BAMBOO_PORT = 8085                  # port for Bamboo Application

f = open("log.txt", "w")                                                # instantiate log file
f.write("Git Update Logs. Created {}\n\n".format(datetime.now()))
f = open("log.txt", "a+")

# basic get request function
# params: {url: url endpoint for GET request}
# return: json response component for request
def get_request(url):
    URL = url
    PARAMS = {}
    HEADERS = {
        'Authorization': AUTH_TOKEN
    }
    r = requests.get(url=URL, params=PARAMS, headers=HEADERS)
    return r.json()

# helper function to find specific repo in a repo_list json
# params: {repo_list: iterable json object consisting of repo objects, repo: name of target repo}
# return repo object or None
def find_repo(repo_list, repo):
    for r in repo_list:
        if (r['slug'] == repo):
            return r
    return None

# helper function to find specific branch in repo json
# params: {repo: iterable json object consisting of repo branches, target_branch: name of target branch}
# return repo object or None
def find_branch(repo, target_branch):
    for b in repo:
        if (b['name'] == target_branch):
            return b
    return None

# main scripting logic
# params: {
#       repo_list: json object consisting of repo objects
#       production_branch: current production branch (target branch)
#       release_branch: latest release (source branch)
#       target_env: target environment for deployment
# }
# return: None
def repo_iterate(repo_list, production_branch, release_branch, target_env):
    for r in repo_list['values']:
        print("Checking repo <{}>".format(r['name']))
        #f.write("Checking repo <{}>\n".format(r['name']))

        branch_url = r['links']['branches']['href']
        res = get_request(branch_url)
        branch = res['values']
        if (find_branch(branch, release_branch) != None): # if release_branch exists
            pull_url = r['links']['pullrequests']['href']
            if (r['name'] == "adapter-gwcc-v1"):
                pull_res = make_pull_request(pull_url, release_branch, production_branch)
        else:
            # bamboo stuff
            production_check(r, target_env)
            print("Project release branch <{}> doesn't exist".format(release_branch))
        print("=============")
    if ('next' in repo_list):
        next_url = repo_list['next']
        next_repo = get_request(next_url)
        repo_iterate(next_repo, production_branch, release_branch, target_env)

# check Bamboo - compare production release and environment release
def production_check(repo, target_env):
    # get production release env for repo
    # from release env, get branch a

    # get release for repo at target_env
    # from relase env, get branch b

    # if branch a != branch b:
        # deploy production_branch into target_env
    pass

def deploy_release(target_env, release):
    # deploy production_branch into target_env
    pass


# makes a POST request to BitBucket API - requests a pull request
# params: { 
#       pull_url: api url to make a pull request for a given repo, 
#       source_branch: source branch in pull request, 
#       dest_branch: destination branch in pull request
# }
# return: True if request made, False if request failed
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
    if (response.status_code == 400):       # return relevant message for pull request failure (no changes, branch not exist, etc.)
        data = response.json()
        message = data['error']['message']
        print(message)
        return False

    if (response.status_code == 201):
        print('Pull request successfully created.') 
        res = response.json()
        diff_link = res['links']['diff']['href']
        conflict = detectConflict(diff_link)

        f.write("Pull request for repo <{}>\n".format(res['destination']['repository']['full_name']))
        f.write("Made pull request from <{}> to <{}>\n".format(source_branch, dest_branch))
        if (conflict):
            f.write("MERGE CONFLICT IN PULL REQUEST\n")
        f.write("Pull request can be found at: {}\n".format(res['links']['html']['href']))
        f.write("===========================\n")
        return True   
    
    return False

# detect if a conflict exists in a pull request
# param: {pr_diff_url: api url to get the diff of a pull request}
# return: True if conflict, otherwise False
def detectConflict(pr_diff_url):
    HEADERS = {
        'Authorization': AUTH_TOKEN
    }
    r = requests.get(url=pr_diff_url, headers=HEADERS)
    diff = r.text
    if "<<<<<<<" in diff:
        print("Merge conflicts in pull request")
        return True
    return False

# helper function to generate string to serve as pull request title
def gen_pull_title(source_branch, dest_branch):
    return "Retrofit from {} into {}".format(source_branch, dest_branch)


# main function (handle command line args)
if __name__ == "__main__":
    if (len(sys.argv) < 3):
        sys.exit('Usage: python3 git-update.py <target_env> <production_branch> [<release_branch>]')

    target_env = sys.argv[1]
    production_branch = sys.argv[2]
    if (len(sys.argv) == 4):
        release_branch = sys.argv[3]
    else:
        release_branch = "master"    

    repos = get_request(REPO_URL)
    repo_iterate(repos, production_branch, release_branch, target_env)
    print("Finished retrofit")
    print("See all changes made in log.txt")
    f.close()