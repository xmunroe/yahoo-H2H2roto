from yahoo_oauth import OAuth1
from myql.utils import pretty_json
from myql import MYQL
from stat_ids import stat_ids
import csv
import os

# read in consumer secret and key
# only consumer_key and consumer_secret are required.
oauth = OAuth1(None, None, from_file='credentials.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

yql = MYQL(format='json', oauth=oauth)

# get league key info from yahoo
response = yql.raw_query('select * from fantasysports.leagues where use_login=1 and game_key in ("mlb")')
r = response.json()
# if in multiple leagues will need to adjust these lines to make sure you're grabbing the right data.
league_key = r['query']['results']['league'][0]['league_key']
num_teams = int(r['query']['results']['league'][0]['num_teams'])
print league_key

teamid = range(1,(num_teams + 1))
rotostats = {}
first = 0
for i in teamid:
    team_key = league_key + '.t.' + str(i)
    stats_query = "select * from fantasysports.teams.stats where team_key='" + team_key +"'"
    response = yql.raw_query(stats_query)
    response = response.json()
    rotostats['teamname'] = str(response['query']['results']['team']['name'])
    rotostats['teamid'] = int(response['query']['results']['team']['team_id'])
    stats = response['query']['results']['team']['team_stats']['stats']['stat']
    for x in stats:
        for y in x:
            if x['stat_id'] != '60':
                rotostats[stat_ids[int(x['stat_id'])]] = float(x['value']) if '.' in x['value'] else int(x['value'])
    #Convert IP base 3 to base 10
    rotostats['IP'] = rotostats['IP'] // 1 + ((10*(rotostats['IP'] % 1))/3)
    rotostats["K/9"] = 9*(rotostats['Ks']/rotostats['IP'])
    print rotostats
    with open("stats.csv", "a") as myFile:
        myFileWriter = csv.DictWriter(myFile, rotostats.keys())
        if first == 0:
            myFileWriter.writeheader()
            first += 1
        myFileWriter.writerow(rotostats)
