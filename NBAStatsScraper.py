# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
import functools as ft

def get_standings(years):
    headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}
    
    # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
    stats = []
    
    # Definim les columnes en funció de les de la taula que volem scrapejar:
    cols = ["wins", "losses", "win_loss_pct", "gb", "pts_per_g", "opp_pts_per_g", "srs"]


    # Comencem el loop per cada temporada:
    for year in years:
        # La url variarà en funció de l'any:
        url = f"http://www.basketball-reference.com/leagues/NBA_{year}.html"
        response = requests.get(url, headers=headers)
        
        # Creem l'objecte Beautiful Soup:
        nba = BeautifulSoup(response.content, 'html.parser')
        
        # Agafem les taules que ens interessen: conferència est i oest.
        eastTable = nba.find(name = "table", attrs = {"id" : "divs_standings_E"})
        westTable = nba.find(name = "table", attrs = {"id" : "divs_standings_W"})
        
        # En temporades antigues no hi ha conferències: 
        preConfTable = nba.find(name = "table", attrs = {"id" : "divs_standings_"})
        
        # Fem la llista amb les taules per a iterar:
        tables = [eastTable, westTable, preConfTable]
        for table in tables:
            # Aquest Try-Catch està pensat per si és una temporada antiga i no
            # hi ha conferències i, per tant, no existeix aquesta taula i no
            # trobaríem cap 'tr'. Per això, fem continue per anar a la següent taula:
            try:
                # Busquem tots els 'tr' d'aquestes taules, on hi ha les informacions
                # dels equips
                for row in table.find_all('tr'):
                    # Creem un diccionari on guardarem les estadístiques de cada
                    # equip a cada temporada:
                    team = {}
                    
                    # Un nou try-catch per evitar les files 'tr' associades a la
                    # divisió de l'equip. Aquestes no tenen valors 'td', així que
                    # no ens interessa. 
                    try:
                        # Agafem les dades que ens interessen:
                        team['Season'] = f"{year-1}/{year}"
                        team['Team'] = row.find('th', {'data-stat' : 'team_name'}).text
                        for col in cols:
                            team[col] = row.find('td', {'data-stat' : col}).text
                        team['Playoffs'] = "Yes" if "*" in team['Team'] else "No"
                    except AttributeError:
                        continue 
                    
                    # Annexem les dades a la llista que hem creat prèviament:
                    stats.append(team)
            except AttributeError:
                continue
        # Deixem uns segons de descans al servidor entre temporada i temporada:
        sleep(randint(1, 5))
    
    # Generem el dataframe amb les estadístiques que hem recollit:
    standings = pd.DataFrame(stats)
    
    # Traiem l'asterisc que indica classificació a playoffs del nom de l'equip,
    # ja que ja tenim una columna que ho referencia. 
    standings['Team'] = standings['Team'].map(lambda x: x.rstrip('*'))
    return standings


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

df1 = get_standings(range(1950, 1955, 1))
df2 = get_advanced_stats(range(1950, 1955, 1))
df3 = get_per_game_stats(range(1950, 1955, 1))

prova = df1.merge(df2, on= ['Season', 'Team', 'wins', 'losses', 'srs']).merge(df3, on = ['Season', 'Team'])

prova.to_csv("provaMerge.csv", index=False)