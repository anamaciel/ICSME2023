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

def get_data_issues(owner, name, number):
    #url = 'https://api.github.com/repos/{}/{}/pulls/{}?access_token={}'.format(owner, name, str(number), "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")
    #url = 'https://api.github.com/repos/{}/{}/issues/{}?{}:{}'.format(owner, name, str(number),client_id,client_secret)
    url = 'https://api.github.com/repos/{}/{}/issues/{}'.format(owner, name, str(number))
    print("URL ISSUE:", url)
    session = requests.Session()
    session.auth = (username, token)
    verify_rate_limit()
    response = session.get(url)
    data = response.json()
    issue = {}
    issue['id'] = data['id']
    issue['owner'] = owner
    issue['name'] = name
    issue['number'] = data['number']
    issue['url'] = data['url']
    issue['title'] = data['title']
    issue['body'] = data['body']
    issue['state'] = data['state']
    issue['locked'] = data['locked']
    issue['active_lock_reason'] = data['active_lock_reason']
    issue['comments'] = data['comments']
    issue['user_login'] = data['user']['login']
    issue['user_id'] = data['user']['id']
    issue['user_type'] = data['user']['type']
    issue['created_at'] = data['created_at']
    issue['updated_at'] = data['updated_at']
    issue['closed_at'] = data['closed_at']
    issue['closed_by'] = data['closed_by']
    issue['author_association'] = data['author_association']
    issue['reactions_total'] = data['reactions']['total_count']
    issue['reactions_+1'] = data['reactions']['+1']
    issue['reactions_-1'] = data['reactions']['-1']
    issue['reactions_laugh'] = data['reactions']['laugh']
    issue['reactions_hooray'] = data['reactions']['hooray']
    issue['reactions_confused'] = data['reactions']['confused']
    issue['reactions_heart'] = data['reactions']['heart']
    issue['reactions_rocket'] = data['reactions']['rocket']
    issue['reactions_eyes'] = data['reactions']['eyes']

    return issue

def collect_repo_infos(owner, name):
    #url = 'https://api.github.com/repos/{}/{}?access_token={}'.format(owner, name, "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")
    #client_id = my_client_id & client_secret = my_secret_id
    #https://api.github.com/repos/vercel/next.js?client_id=anamaciel&client_secret=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
    #url = "https://api.github.com/repos/{}/{}?{}:{}".format(owner, name, client_id,client_secret)
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

def collect_issues(owner, name):

    repo_id = collect_repo_infos(owner, name)

    #page = 121
    page = 1
    last_page = False
    while not last_page:
        print('Page {}'.format(page))

        url = 'https://api.github.com/repos/{}/{}/issues?page={}'.format(owner, name, page)
        #url = 'https://api.github.com/repos/{}/{}/issues?state=closed&page={}'.format(owner, name,page)
        print("URL PAGE:",url)
        session = requests.Session()
        session.auth = (username, token)
        verify_rate_limit()
        response = session.get(url)
        data_all = response.json()


        for data in data_all:
            issue = get_data_issues(owner, name, data['number'])
            issue['repo_id'] = repo_id
            db.issues.insert_one(issue)

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
        print("name",owner)

        print('Collecting... {} {}'.format(owner, __name__))

        collect_issues(owner, name)
