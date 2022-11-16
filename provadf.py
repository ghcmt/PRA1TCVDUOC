import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}

url = "http://www.basketball-reference.com/leagues/NBA_1992.html"
response = requests.get(url, headers=headers)
nba = BeautifulSoup(response.content, 'html.parser')       
eastTable = nba.find(name = "table", attrs = {"id" : "divs_standings_E"})
stats = []
for row in eastTable.find_all('tr')[2:]:
    team = {}
    try:
        team['Name'] = row.find('th', {'data-stat' : 'team_name'}).text
        team['Wins'] = row.find('td', {'data-stat' : 'wins'}).text
        team['Losses'] = row.find('td', {'data-stat' : 'losses'}).text
        team['WinLossPct'] = row.find('td', {'data-stat' : 'win_loss_pct'}).text
        team['GamesBehind'] = row.find('td', {'data-stat' : 'gb'}).text
        team['PointsPerGame'] = row.find('td', {'data-stat' : 'pts_per_g'}).text
        team['PointsAgainstPerGame'] = row.find('td', {'data-stat' : 'opp_pts_per_g'}).text
        team['SRS'] = row.find('td', {'data-stat' : 'srs'}).text
        team['Playoffs'] = "Yes" if "*" in team['Name'] else "No"    
    except AttributeError:
        continue   
    stats.append(team)

east = pd.DataFrame(stats)
east.to_csv("prova.csv", index=False)
