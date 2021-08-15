import requests
import json
from os import getenv
import re

GH_TOKEN = getenv("GH_TOKEN")
repo_regex = re.compile("https://github.com/[\w\.@\:\-~]+/[\w\.@\:\-~]+")

# create list of tested addons
tested = repo_regex.findall(open("MeteorAddons.md", "r", encoding='utf-8').read())
tested = set(tested)
print(f"Found tested addons: {len(tested)}")

# get template size & name
r = requests.get("https://api.github.com/repos/MeteorDevelopment/meteor-addon-template")
repo = r.json()
template_name = repo["name"]
template_size = repo["size"]
del repo

# function that formats repos contents to exclute private and tested repos and repos which are just unmodified templates and add code size property
def parse_repo(repo):
    if repo['private']:
        return None
    if repo['html_url'] in tested:
        return None
    if repo['name'] == template_name:
        return None
    if repo['size'] == template_size:
        return None
    r = requests.get(repo['url'])
    repo.update(r.json())
    return repo

# Request all code snippets in java extending MeteorAddon class
r = requests.get(f"https://api.github.com/search/code?q=extends+MeteorAddon+language:java+in:file+fork:true&per_page=100&access_token={GH_TOKEN}")
repos = r.json()['items']
repos = [repo['repository'] for repo in repos]

# Request all forks of meteor-addon-template because some people cant click generate
r = requests.get("https://api.github.com/repos/MeteorDevelopment/meteor-addon-template/forks?per_page=100")
repos.extend(r.json())

# load repos
repos = [parse_repo(repo) for repo in repos]
repos = list(filter(bool, repos))
repos.sort(key=lambda x: x['size'], reverse=True)

# create markdown file, write template to it
file = open("UntestedAddons.md", 'w+', encoding='utf-8')
file.write(open("res/UntestedAddons.template.md", "r", encoding='utf-8').read())

# add a line for each repo
for repo in repos:
    print(f"Adding: {repo['full_name']}")
    file.write(f"\n| {repo['name']} | {repo['description']} | [Repository]({repo['html_url']}) | {repo['owner']['login']} |")

file.close()