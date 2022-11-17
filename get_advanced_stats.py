import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint

def get_advanced_stats(years):    
    headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}
    
    # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
    stats = []
    
    # Definim les columnes en funció de les de la taula que volem scrapejar:
    cols = ['age', 'wins', 'losses', 'wins_pyth', 'losses_pyth', 'mov', 'sos', 
            'srs', 'off_rtg', 'def_rtg', 'net_rtg', 'pace', 'fta_per_fga_pct', 
            'fg3a_per_fga_pct', 'ts_pct', 'efg_pct', 'tov_pct', 'orb_pct', 
            'ft_rate', 'opp_efg_pct', 'opp_tov_pct', 'drb_pct', 'opp_ft_rate', 
            'attendance', 'attendance_per_g']


    # Comencem el loop per cada temporada:
    for year in years:
        # La url variarà en funció de l'any:
        url = f"http://www.basketball-reference.com/leagues/NBA_{year}.html"
        response = requests.get(url, headers=headers)
        
        # Creem l'objecte Beautiful Soup:
        nba = BeautifulSoup(response.content, 'html.parser')
        
        # Busquem la taula:
        advTable = nba.find_all('table', {'id': 'advanced-team'})
    
        for row in advTable[0].find_all('tr'):    
            team = {}
            try:
                team['Season'] = f"{year-1}/{year}"
                team['Team'] = (row.find('td', {'data-stat' : 'team'}).text)    
                for col in cols:
                    team[col] = row.find('td', {'data-stat' : col}).text
    
            except AttributeError:
                continue   
            stats.append(team)     
        sleep(randint(1, 5))
 
    # Generem el dataframe amb les estadístiques que hem recollit:
    advanced = pd.DataFrame(stats)
    
    # Traiem l'asterisc que indica classificació a playoffs del nom de l'equip,
    # ja que ja tenim una columna que ho referencia. 
    advanced['Team'] = advanced['Team'].map(lambda x: x.rstrip('*'))
    return advanced

get_advanced_stats(range(1950, 1955, 1)).to_csv("provaGetAdvancedStats.csv", index=False)