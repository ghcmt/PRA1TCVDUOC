import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint

def get_per_game_stats(years):    
    headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}
    
    # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
    stats = []
    
    # Definim les columnes en funció de les de la taula que volem scrapejar:
    cols = ['g', 'mp', 'fg', 'fga', 'fg_pct', 'fg3', 'fg3a', 'fg3_pct',
            'fg2', 'fg2a', 'fg2_pct', 'ft', 'fta', 'ft_pct', 'orb', 'drb',
            'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']


    # Comencem el loop per cada temporada:
    for year in years:
        # La url variarà en funció de l'any:
        url = f"http://www.basketball-reference.com/leagues/NBA_{year}.html"
        response = requests.get(url, headers=headers)
        
        # Creem l'objecte Beautiful Soup:
        nba = BeautifulSoup(response.content, 'html.parser')

        pGTable = nba.find_all('table', {'id': 'per_game-team'})
    
        for row in pGTable[0].find_all('tr')[:-1]:    
            team = {}
            try:
                team['Season'] = f"{year-1}/{year}"
                team['Team'] = row.find('td', {'data-stat' : 'team'}).text    
                for col in cols:
                    team[col] = row.find('td', {'data-stat' : col}).text
    
            except AttributeError:
                continue   
            stats.append(team)     
        sleep(randint(1, 5))
 
    # Generem el dataframe amb les estadístiques que hem recollit:
    perGame = pd.DataFrame(stats)
    
    # Traiem l'asterisc que indica classificació a playoffs del nom de l'equip,
    # ja que ja tenim una columna que ho referencia. 
    perGame['Team'] = perGame['Team'].map(lambda x: x.rstrip('*'))
    return perGame

get_per_game_stats(range(1950, 1955, 1)).to_csv("provaGetPerGameStats.csv", index=False)
