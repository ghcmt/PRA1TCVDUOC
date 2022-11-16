import requests
from bs4 import BeautifulSoup
import re
import csv
import bs4
import pandas as pd #pels dataframes
from time import sleep #ho haurem de posar per fer-ho server-friendly

def get_conference_data(soup, conference):

    if(conference == 'Eastern'):
        id = 'divs_standings_E'

    elif(conference == 'Western'):
        id = 'divs_standings_W'

    else:
        return "Error (Bad Conference)"

    table_content = soup.find_all('table', {'id': id})
 
    cols = ['wins', 'losses', 'win_loss_pct', 'gb', 'pts_per_g', 'opp_pts_per_g', 'srs']

    stats = []
    for row in table_content[0].find_all('tr')[1:]:
        team = {}
        try:
            team['Team'] = row.find('th', {'data-stat' : 'team_name'}).text

            for col in cols:
                team[col] = row.find('td', {'data-stat' : col}).text
                
            team['Playoffs'] = "Yes" if "*" in team['Team'] else "No"
            team['Team'] = team['Team'].replace('*','')
        except AttributeError:
            continue   
        stats.append(team)

    return stats

def get_per_game_stats(soup):

    table_content = soup.find_all('table', {'id': 'per_game-team'})

    cols = ['g', 'mp', 'fg', 'fga', 'fg_pct', 'fg3', 'fg3a', 'fg3_pct',
            'fg2', 'fg2a', 'fg2_pct', 'ft', 'fta', 'ft_pct', 'orb', 'drb',
            'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']

    stats = []
    for row in table_content[0].find_all('tr')[1:-1]:

        team = {}
        try:
            team['Team'] = (row.find('td', {'data-stat' : 'team'}).text).replace('*','')

            for col in cols:
                team[col] = row.find('td', {'data-stat' : col}).text

        except AttributeError:
            continue   
        stats.append(team)

    return stats
    

def merge_data(season_data, conference_data, per_game_stats_data):

    for per_game_team_stats in per_game_stats_data:
        for conference_team in conference_data:
            # Mirem els equips per tal de juntar dades
            if(conference_team['Team'] in per_game_team_stats['Team']):
                per_game_team_stats.update(conference_team)
                per_game_team_stats['Season'] = season_data[0]
                per_game_team_stats['League'] = season_data[1]

    return per_game_stats_data


def get_nba_aba_league_data(base_link):

    page = requests.get(base_link + '/leagues/')
    soup = BeautifulSoup(page.text, 'html.parser')

    table_content = soup.find_all('table', {'id': 'stats'})
 
    all_seasons = []
    seasons_info = []
    seasons_links = []

    cols = ['lg_id', 'champion', 'mvp', 'roy', 'pts_leader_name', 
            'trb_leader_name', 'ast_leader_name', 'ws_leader_name']

    for row in table_content[0].find_all('tr')[3:]:
        season = {}
        try:
            season['season'] = row.find('th', {'data-stat' : 'season'}).text

            for col in cols:
                season[col] = row.find('td', {'data-stat' : col}).text
            
            seasons_links.append(base_link + row.find('a', href=True)['href'])

        except AttributeError:
            continue

        seasons_info.append([season['season'], season['lg_id']])
        all_seasons.append(season)

    return [all_seasons, seasons_links, seasons_info]


def data_to_csv(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)

if __name__ == "__main__":

    base_link = 'https://www.basketball-reference.com'
    all_seasons, seasons_links, season_info = get_nba_aba_league_data(base_link)

    data_to_csv(all_seasons, 'overall_info.csv')

    seasons_links = ['https://www.basketball-reference.com/leagues/NBA_2019.html']
    season_info = [["2018-2019", "NBA"]]

    for link, season_info in zip(seasons_links, season_info):

        page = requests.get(link, headers = {'User-Agent': 'PRA1UOC'}) 

        soup = BeautifulSoup(page.text, 'html.parser')

        eastern_data = get_conference_data(soup, "Eastern")
        western_data = get_conference_data(soup, "Western")
        
        conference_data = eastern_data + western_data

        per_game_data = get_per_game_stats(soup)

        data = merge_data(season_info, conference_data, per_game_data)
        
        data_to_csv(data, 'seasons_data.csv')
        
