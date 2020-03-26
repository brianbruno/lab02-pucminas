import requests
from radon.raw import analyze
import git
import os

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
    the_file.write('stars,watchers,forks,loc,releases,releases_frequency,age\n'
                   '')

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

    print(analyze(dir_name+'/'+node['name']))


    with open("repos.csv", 'a') as the_file:
        the_file.write(str(node['stargazers']['totalCount']) + "," + str(node['watchers']['totalCount']) + "," + str(node['forks']['totalCount']) + ","
                       '0,' + str(node['releases']['totalCount']) + ',' + 'frequencia,' + 'idade' + "\n")