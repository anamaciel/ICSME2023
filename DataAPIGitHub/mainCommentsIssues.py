import requests
import csv
import pymongo
import json
import os
from datetime import datetime
import time

#ACCESS_TOKEN = os.environ['TOKEN_GITHUB_PULLS']

client = pymongo.MongoClient("localhost", 27017)
db = client.directusDirectus

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


def get_data_issues(owner, name, number):
    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments'.format(owner, name, str(number))

    session = requests.Session()
    session.auth = (username, token)
    verify_rate_limit()
    response = session.get(url)
    data = response.json()

    for dataComment in data:
        comment = {}
        comment['id'] = dataComment['id']
        comment['issue'] = dataComment['issue_url']
        comment['user_login'] = dataComment['user']['login']
        comment['user_type'] = dataComment['user']['type']
        comment['created_at'] = dataComment['created_at']
        comment['updated_at'] = dataComment['updated_at']
        comment['author_association'] = dataComment['author_association']
        comment['body'] = dataComment['body']
        comment['reactions_total'] = dataComment['reactions']['total_count']
        comment['reactions_+1'] = dataComment['reactions']['+1']
        comment['reactions_-1'] = dataComment['reactions']['-1']
        comment['reactions_laugh'] = dataComment['reactions']['laugh']
        comment['reactions_hooray'] = dataComment['reactions']['hooray']
        comment['reactions_confused'] = dataComment['reactions']['confused']
        comment['reactions_heart'] = dataComment['reactions']['heart']
        comment['reactions_rocket'] = dataComment['reactions']['rocket']
        comment['reactions_eyes'] = dataComment['reactions']['eyes']

        db.issuesComments.insert_one(comment)


def collect_repo_infos(owner, name):
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

    # db.repos.insert_one(repo)

    return repo['id']

def collect_issues(owner, name):
    repo_id = collect_repo_infos(owner, name)

    # page = 1612
    page = 1
    last_page = False
    while not last_page:
        print('Page {}'.format(page))

        #url = 'https://api.github.com/repos/{}/{}/issues?state=closed&page={}'.format(owner, name, page)
        url = 'https://api.github.com/repos/{}/{}/issues?page={}'.format(owner, name, page)
        session = requests.Session()
        session.auth = (username, token)
        verify_rate_limit()
        response = session.get(url)
        data_all = response.json()

        for data in data_all:
            get_data_issues(owner, name, data['number'])
            # pull = get_data_issues(owner, name, data['number'])
            # pull['repo_id'] = repo_id
            # db.pulls.insert_one(pull)

        if 'Link' not in response.headers or 'rel="next"' not in response.headers['Link']:
            last_page = True
        else:
            page = page + 1


if __name__ == '__main__':

    projects_file = open('C:/Users/anacm/Documents/DOUTORADO/GITHUB/coletaDiscussions/IssuesPR/projects.csv', 'r')
    reader_projects = csv.reader(projects_file, delimiter=',')
    
    
    for row in reader_projects:
        owner = row[0]
        name = row[1]
        print("owner",owner)
        print("name",owner)

        print('Collecting... {} {}'.format(owner, __name__))

        collect_issues(owner, name)
