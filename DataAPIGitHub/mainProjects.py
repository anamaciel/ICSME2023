import requests
import csv
import pymongo
import json
import os
from datetime import datetime
import time

#ACCESS_TOKEN = os.environ['TOKEN_GITHUB_PULLS']

client = pymongo.MongoClient("localhost", 27017)
db = client.ALLprojects

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

def collect_repo_infos(owner, name):
    #url = 'https://api.github.com/repos/{}/{}?access_token={}'.format(owner, name, "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")
    #client_id = my_client_id & client_secret = my_secret_id
    #https://api.github.com/repos/vercel/next.js?client_id=anamaciel&client_secret=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
    #url = "https://api.github.com/repos/{}/{}?{}:{}".format(owner, name, client_id,client_secret)
    url = 'https://api.github.com/repos/{}/{}'.format(owner, name)
    print(url)
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
    repo['created_at'] = data['created_at']
    repo['fork'] = data['fork']
    repo['forks'] = data['forks']
    repo['stars'] = data['stargazers_count']
    repo['watchers'] = data['watchers_count']
    repo['forks'] = data['forks_count']
    repo['language'] = data['language']
    repo['owner_type'] = data['owner']['type']
    repo['homepage'] = data['homepage']
    repo['size'] = data['size']
    repo['open_issues_count'] = data['open_issues_count']
    repo['network_count'] = data['network_count']
    repo['subscribers_count'] = data['subscribers_count']

    num_pulls = 0
    page = 1
    last_page = False
    while not last_page:
        print('Page {}'.format(page))

        url = 'https://api.github.com/repos/{}/{}/pulls?state=all&page={}&per_page=100'.format(owner, name, page)
        print("URL PAGE:", url)
        session = requests.Session()
        session.auth = (username, token)
        verify_rate_limit()
        response = session.get(url)
        data_all = response.json()

        for data in data_all:
            num_pulls = num_pulls + 1

        if 'Link' not in response.headers or 'rel="next"' not in response.headers['Link']:
            last_page = True
        else:
            page = page + 1
    repo['pulls_count'] = num_pulls

    num_issues = 0
    page = 1
    last_page = False
    while not last_page:
        print('Page {}'.format(page))

        url = 'https://api.github.com/repos/{}/{}/issues?state=all&page={}&per_page=100'.format(owner, name, page)
        print("URL PAGE:", url)
        session = requests.Session()
        session.auth = (username, token)
        verify_rate_limit()
        response = session.get(url)
        data_all = response.json()

        for data in data_all:
            num_issues = num_issues + 1

        if 'Link' not in response.headers or 'rel="next"' not in response.headers['Link']:
            last_page = True
        else:
            page = page + 1
    repo['issues_count'] = num_issues

    num_contributors=0
    page = 1
    last_page = False
    while not last_page:
        print('Page {}'.format(page))

        url = 'https://api.github.com/repos/{}/{}/contributors?page={}'.format(owner, name, page)
        print("URL PAGE:", url)
        session = requests.Session()
        session.auth = (username, token)
        verify_rate_limit()
        response = session.get(url)
        data_all = response.json()

        for data in data_all:
            num_contributors=num_contributors+1

        if 'Link' not in response.headers or 'rel="next"' not in response.headers['Link']:
            last_page = True
        else:
            page = page + 1
    repo['num_contributors'] = num_contributors
    print(repo)

    db.repos.insert_one(repo)

    return repo['id']

if __name__ == '__main__':

    projects_file = open('C:/Users/anacm/Documents/DOUTORADO/GITHUB/coletaDiscussions/IssuesPR/reposColeta.csv', 'r')
    reader_projects = csv.reader(projects_file, delimiter=';')
    
    
    for row in reader_projects:
        owner = row[0]
        name = row[1]
        print("owner",owner)
        print("name",owner)

        print('Collecting... {} {}'.format(owner, __name__))

        collect_repo_infos(owner, name)
