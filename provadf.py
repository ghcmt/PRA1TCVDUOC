import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}

url = "http://www.basketball-reference.com/leagues/NBA_2016.html"
response = requests.get(url, headers=headers)
nba = BeautifulSoup(response.content, 'html.parser')       
eastTable = nba.find(name = "table", attrs = {"id" : "divs_standings_E"})
westTable = nba.find(name = "table", attrs = {"id" : "divs_standings_W"})
stats = []
cols = ["wins", "losses", "win_loss_pct", "gb", "pts_per_g", "opp_pts_per_g", "srs"]
tables = [eastTable, westTable]

for table in tables:
    for row in table.find_all('tr')[2:]:
        team = {}
        try:
            team['Year'] = 2016
            team['Name'] = row.find('th', {'data-stat' : 'team_name'}).text
            for col in cols:
                team[col] = row.find('td', {'data-stat' : col}).text
            team['Playoffs'] = "Yes" if "*" in team['Name'] else "No"
        except AttributeError:
            continue   
        stats.append(team)


standings = pd.DataFrame(stats)
standings.to_csv("prova.csv", index=False)
