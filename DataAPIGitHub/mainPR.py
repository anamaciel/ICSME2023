import requests
import csv
import pymongo
import json
import os
from datetime import datetime
import time

#ACCESS_TOKEN = os.environ['TOKEN_GITHUB_PULLS']

client = pymongo.MongoClient("localhost", 27017)
db = client.issuesALLprojects

username=""
token=""

def verify_rate_limit():
    session = requests.Session()
    session.auth = (username, token)
    response = session.get('https://api.github.com/rate_limit')
    data_all = response.json()

    rate_limit_remaining = int(data_all['resources']['core']['remaining'])
    rate_limit_reset = int(data_all['resources']['core']['reset'])
    remaining_seconds=0
    reset_time = 0
    current_time = 0
    datetime_format = '%Y-%m-%d %H:%M:%S'
    reset_time = datetime.fromtimestamp(rate_limit_reset).strftime(datetime_format)
    current_time = datetime.now().strftime(datetime_format)
    remaining_seconds = (datetime.fromtimestamp(rate_limit_reset) - datetime.now()).total_seconds() + 5
    if rate_limit_remaining>1:
        #print(remaining_seconds)
        print('[API] Requests Remaining: {}'.format(rate_limit_remaining))
    else:
         print('The request limit is over. The process will sleep for %d seconds.' % remaining_seconds)
         print('The request limit will reset on: {}'.format(reset_time))
         time.sleep(remaining_seconds)

def get_data(owner, name, number):
    #url = 'https://api.github.com/repos/{}/{}/pulls/{}?access_token={}'.format(owner, name, str(number), "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")
    #url = 'https://api.github.com/repos/{}/{}/issues/{}'.format(owner, name, str(number))

    url = 'https://api.github.com/repos/{}/{}/pulls/{}'.format(owner, name, str(number))
    print(url)
    session = requests.Session()
    session.auth = (username, token)
    verify_rate_limit()
    response = session.get(url)
    data = response.json()

    pull = {}
    pull['id'] = data['id']
    pull['owner'] = owner
    pull['name'] = name
    pull['number_pr'] = data['number']
    pull['state'] = data['state']
    pull['locked'] = data['locked']
    pull['title'] = data['title']
    pull['body'] = data['body']
    pull['user'] = data['user']['login']
    pull['user_type'] = data['user']['type']
    pull['review_comments'] = data['review_comments']
    pull['commits'] = data['commits']
    pull['additions'] = data['additions']
    pull['deletions'] = data['deletions']
    pull['changed_files'] = data['changed_files']
    pull['created_at'] = data['created_at']
    pull['updated_at'] = data['updated_at']
    pull['merged_at'] = data['merged_at']
    pull['closed_at'] = data['closed_at']

    return pull

def collect_repo_infos(owner, name):
    #url = 'https://api.github.com/repos/{}/{}?access_token={}'.format(owner, name, "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")
    #url = 'https://api.github.com/repos/{}/{}'.format(owner, name)
    #print(url)

    url = 'https://api.github.com/repos/{}/{}'.format(owner, name)
    session = requests.Session()
    session.auth = (username, token)
    verify_rate_limit()
    response = session.get(url)

    data = response.json()
    repo = {}
    repo['id'] = data['id']
    repo['owner'] = owner
    repo['name'] = name
    repo['full_name'] = data['full_name']
    repo['fork'] = data['fork']
    repo['stars'] = data['stargazers_count']
    repo['language'] = data['language']

    #db.repos.insert_one(repo)

    return repo['id']

def collect_pulls(owner, name):

    repo_id = collect_repo_infos(owner, name)

    #page = 164
    page = 1
    last_page = False
    while not last_page:
        print('Page {}'.format(page))

        #url = 'https://api.github.com/repos/{}/{}/pulls?state=closed&page={}'.format(owner, name, page)
        url = 'https://api.github.com/repos/{}/{}/pulls?page={}'.format(owner, name, page)
        print(url)
        session = requests.Session()
        session.auth = (username, token)
        verify_rate_limit()
        response = session.get(url)
        data_all = response.json()


        for data in data_all:
            pull = get_data(owner, name, data['number'])
            pull['repo_id'] = repo_id
            db.pulls.insert_one(pull)

        if 'Link' not in response.headers or 'rel="next"' not in response.headers['Link']:
            last_page = True
        else:
            page = page + 1


if __name__ == '__main__':

    projects_file = open('C:/Users/anacm/Documents/DOUTORADO/GITHUB/coletaDiscussions/IssuesPR/reposColeta.csv', 'r')
    reader_projects = csv.reader(projects_file, delimiter=';')
    
    
    for row in reader_projects:
        owner = row[0]
        name = row[1]
        print("owner",owner)
        print("name",name)

        print('Collecting... {} {}'.format(owner, __name__))

        collect_pulls(owner, name)
