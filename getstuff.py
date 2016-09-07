from yahoo_oauth import OAuth1
from myql.utils import pretty_json
from myql import MYQL
from stat_ids import stat_ids
import csv
import os

myPath = "/Users/xander/python_test/roto/"
#read in consumer secret and key
oauth = OAuth1(None, None, from_file='credentials.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

yql = MYQL(format='json', oauth=oauth)

response = yql.raw_query('select * from fantasysports.leagues where use_login=1 and game_key in ("mlb")')
r = response.json()
league_key = r['query']['results']['league'][0]['league_key']
print league_key

teamid = range(1,13)
rotostats = {}
first = 0
for i in teamid:
    team_key = league_key + '.t.' + str(i)
    stats_query = "select * from fantasysports.teams.stats where team_key='" + team_key +"'"
    response = yql.raw_query(stats_query)
    response = response.json()
    team_name = str(response['query']['results']['team']['name'])
    stats = response['query']['results']['team']['team_stats']['stats']['stat']
    for x in stats:
        for y in x:
            if x['stat_id'] != '60':
                rotostats[stat_ids[int(x['stat_id'])]] = float(x['value']) if '.' in x['value'] else int(x['value'])
    rotostats["K/9"] = 9*(rotostats['Ks']/rotostats['IP'])
    rotostats['teamname'] = team_name
    print rotostats
    with open(os.path.join(myPath, "stats.csv"), "a") as myFile:
        myFileWriter = csv.DictWriter(myFile, rotostats.keys())
        if first == 0:
            myFileWriter.writeheader()
            first += 1
        myFileWriter.writerow(rotostats)
