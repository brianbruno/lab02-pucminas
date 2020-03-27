import requests
from radon.raw import analyze
import git
import os
import datetime
from datetime import date

def run_query(json, headers): # A simple function to use requests.post to make the API call.

    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))

query = """
{
  search(query:"user:gvanrossum", type:REPOSITORY, first:50)
  {
    pageInfo{
        hasNextPage
        endCursor
    }
    nodes{
      ... on Repository
      {
        name
        owner {
          login
        }
        nameWithOwner
        url
        createdAt
        updatedAt
        primaryLanguage {
          id
          name
        }
        watchers {
          totalCount
        }
        stargazers {
          totalCount
        }
        forks {
          totalCount
        }
        releases
        {
          totalCount
        }
      }
    }
    pageInfo
    {
      endCursor
    }
  }
}
"""

finalQuery = query.replace("{AFTER}", "")

json = {
    "query":finalQuery, "variables":{}
}

token = 'b86bb92aa54dcef4d2b470ecf46ee6a01ac3dc7d' #insert your token
headers = {"Authorization": "Bearer " + token}

total_pages = 1

result = run_query(json, headers)

nodes = result['data']['search']['nodes']

with open("repos.csv", 'a') as the_file:
    the_file.write('name,stars,watchers,forks,loc,releases,releases_by_week,age_weeks\n')

# saving data
for node in result['data']['search']['nodes']:
    if (node['primaryLanguage'] is None):
        primaryLanguage = 'None'
    else:
        primaryLanguage = node['primaryLanguage']['name']

    dir_name = "repositories/"+node['owner']['login']

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    git.Git(dir_name).clone(node['url'])

    totalLoc = 0

    for root, dirs, files in os.walk('repositories/' + node['nameWithOwner']):
        for file in files:
            if file.endswith('.py'):
                fullpath = os.path.join(root, file)
                with open(fullpath, encoding="utf8") as f:
                    content = f.read()
                    b = analyze(content)
                    print(b)
                    i = 0
                    for item in b:
                        if i == 0:
                            totalLoc += item
                            i += 1

    created_date = node['createdAt'][0:10]

    today = date.today()
    date_time_obj = datetime.datetime.strptime(created_date, '%Y-%m-%d').date()

    days = abs(today - date_time_obj).days
    weeks = days // 7
    releases_by_week = node['releases']['totalCount']/weeks

    with open("repos.csv", 'a') as the_file:
        the_file.write(node['nameWithOwner'] + ',' + str(node['stargazers']['totalCount']) + "," + str(node['watchers']['totalCount']) + "," + str(node['forks']['totalCount']) + "," +
                       str(totalLoc) + ',' + str(node['releases']['totalCount']) + ',' + str(releases_by_week) + ',' + str(weeks)  + "\n")