import requests
import time
import traceback

def run_query(json, headers): # A simple function to use requests.post to make the API call.

    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)

    while request.status_code == 502:
        time.sleep(2)
        request = requests.post('https://api.github.com/graphql', json=json, headers=headers)

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))


fileName = 'issues-' + str(int(time.time())) + '.csv'
with open(fileName, 'a') as the_file:
    the_file.write('nameWithOwner,number,state\n')

query = """
{
  search(query:"stars:>100", type:REPOSITORY, first:4 {AFTER})
  {
    pageInfo{
        hasNextPage
        endCursor
    }
    nodes{
      ... on Repository
      {
        nameWithOwner
        url
        issues (first:100, orderBy: { field: CREATED_AT, direction: DESC }) {
          pageInfo{
            hasNextPage
            endCursor
          }
          totalCount
          nodes {
            number            
            state
          }
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

next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]

totalIssues = 0


while next_page and total_pages < 125:
    try:
        print('pages: ' + str(total_pages))
        total_pages += 1
        nodes += result['data']['search']['nodes']

        for node in nodes:

            totalIssues += len(node['issues']['nodes'])

            for issue in node['issues']['nodes']:
                with open(fileName, 'a', encoding="utf-8") as the_file:
                    the_file.write(node['nameWithOwner'] + ',' + str(issue['number']) + ',' + issue['state'] + "\n")

        print('Total de issues: ' + str(totalIssues))

        cursor = result["data"]["search"]["pageInfo"]["endCursor"]
        next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
        json["query"] = next_query
        result = run_query(json, headers)
        next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]

    except Exception as e:
        print('Tentando novamente')
        print(str(e))
        traceback.print_exc()
        time.sleep(10)