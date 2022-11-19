# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
import os


def NBA_scraper(years):
    headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}
    
    # Creem les llistes on guardarem les dades de cada temporada:
    stlist = []
    pGlist = []
    advlist = []
    
    for year in years:    
        # Creem l'objecte Beautiful Soup:
        url = f"http://www.basketball-reference.com/leagues/NBA_{year}.html"
        response = requests.get(url, headers=headers)
        nba = BeautifulSoup(response.content, 'html.parser')
        
        # Cridem a les funcions:
        print(f"Scraping season {year-1}/{year}")
        # Comencem agafant les dades de les classificacions:
        standings = get_standings(nba, year, 
                      ["divs_standings_E", "divs_standings_W", "divs_standings_"],
                      ["wins", "losses", "win_loss_pct", "gb", "pts_per_g", "opp_pts_per_g", 
                       "srs"])
        stlist.append(standings)
        
        # Agafem les dades per partit de cada equip:
        pG = get_per_game_stats(nba, year, 'per_game-team', 
                           ['g', 'mp', 'fg', 'fga', 'fg_pct', 'fg3', 'fg3a', 'fg3_pct',
                'fg2', 'fg2a', 'fg2_pct', 'ft', 'fta', 'ft_pct', 'orb', 'drb',
                'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])
        pGlist.append(pG)
        
        # Finalment, recollim les mètriques avançades:
        adv = get_advanced_stats(nba, year, 'advanced-team', 
                           ['age', 'wins', 'losses', 'wins_pyth', 'losses_pyth', 'mov', 'sos', 
                'srs', 'off_rtg', 'def_rtg', 'net_rtg', 'pace', 'fta_per_fga_pct', 
                'fg3a_per_fga_pct', 'ts_pct', 'efg_pct', 'tov_pct', 'orb_pct', 
                'ft_rate', 'opp_efg_pct', 'opp_tov_pct', 'drb_pct', 'opp_ft_rate', 
                'attendance', 'attendance_per_g'])
        advlist.append(adv)
        
        # Deixem descansar al servidor entre temporada i temporada:
        sleep(randint(5, 10))
        
    # Generem els dataframes amb les dades de les temporades desitjades:
    df1 = pd.concat(stlist)
    df2 = pd.concat(pGlist)
    df3 = pd.concat(advlist)
    
    # Unim els dataframes a partir de les variables comunes:
    finalDF = df1.merge(df3, on= ['Season', 'Team', 'wins', 'losses', 'srs']).merge(df2, on = ['Season', 'Team'])
    
    # Exportem les dades a csv i les guardem en una nova carpeta:
    csvFolder = os.path.join(os.getcwd(), r'data')
    if not os.path.exists(csvFolder):
        os.makedirs(csvFolder)
    
    df1.to_csv(f"./data/Standings{years[0]}_{years[-1]}.csv", index = False)
    df2.to_csv(f"./data/PerGameStats{years[0]}_{years[-1]}.csv", index = False)
    df3.to_csv(f"./data/AdvancedStats{years[0]}_{years[-1]}.csv", index = False)
    finalDF.to_csv(f"./data/AllStats{years[0]}_{years[-1]}.csv", index = False)    
    
    return finalDF
        


def get_standings(soup, year, ids, cols):    
    # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
    stats = []
        
    # Agafem les taules que ens interessen: conferència est i oest.
    tables = []
    for tableId in ids:
        table = soup.find(name = "table", attrs = {"id" : tableId})
        tables.append(table)
        
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
                # no ens interessen. 
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

    # Generem el dataframe amb les estadístiques que hem recollit:
    standings = pd.DataFrame(stats)
    
    # Traiem l'asterisc que indica classificació a playoffs del nom de l'equip,
    # ja que ja tenim una columna que ho referencia. 
    standings['Team'] = standings['Team'].map(lambda x: x.rstrip('*'))
    return standings


def get_per_game_stats(soup, year, ids, cols):       
    # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
    pgStats = []  
    
    # Busquem la taula:
    pGTable = soup.find_all('table', {'id': ids})
    
    # Iterem per treure les estadístiques. Evitem l'última fila perquè conté
    # el 'league average' i no ens interessa:
    for row in pGTable[0].find_all('tr')[:-1]:    
        team = {}
        # Bloc try-catch per només agafar línies que continguin els valors
        # que volem:
        try:
            team['Season'] = f"{year-1}/{year}"
            team['Team'] = row.find('td', {'data-stat' : 'team'}).text    
            for col in cols:
                team[col] = row.find('td', {'data-stat' : col}).text
        except AttributeError:
            continue   
        
        # Finalment, afegim les dades de la temporada a la llista:
        pgStats.append(team)
 
    # Generem el dataframe amb les estadístiques que hem recollit:
    perGame = pd.DataFrame(pgStats)
    
    # Traiem de nou l'asterisc:
    perGame['Team'] = perGame['Team'].map(lambda x: x.rstrip('*'))
    return perGame


def get_advanced_stats(soup, year, ids, cols): 
    # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
    advStats = []  
        
    # Busquem la taula a partir de la id:
    advTable = soup.find_all('table', {'id': ids})
    
    # Iterem per les files i de nou no guardem l'última fila:
    for row in advTable[0].find_all('tr')[:-1]:    
        team = {}
        try:
            team['Season'] = f"{year-1}/{year}"
            team['Team'] = (row.find('td', {'data-stat' : 'team'}).text)    
            for col in cols:
                team[col] = row.find('td', {'data-stat' : col}).text

        except AttributeError:
            continue
        
        # Afegim les dades de cada equip a la llista:
        advStats.append(team)     
 
    # Generem el dataframe amb les estadístiques que hem recollit:
    advanced = pd.DataFrame(advStats)
    
    # Traiem l'asterisc que indica classificació a playoffs:
    advanced['Team'] = advanced['Team'].map(lambda x: x.rstrip('*'))
    return advanced

NBA_scraper(range(1950, 2023, 1))


