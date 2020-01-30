# git-automation
### Git automation project for Deloitte.
---
Tool to automatically track changes between branches.  
Specify a target repo, production_branch and release_branch.  
The script will automatically compare the production_branch and release_branch and make a pull request if there are changes from the release branch that should exist in the the production_branch

## Usage
1. Install python dependencies with `pip` and `requirements.txt`
2. Run script `python3 git-update.py <target_repo> <production_branch> <release_branch>`


NOTE: Files `git-api.js` and `git-update.js` in `test_code` are files from early testing.