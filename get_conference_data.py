import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint

headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}

# Creem una llista on guardarem les estadístiques de la taula per cada temporada:
stats = []

# Definim les columnes en funció de les de la taula que volem scrapejar:
cols = ["wins", "losses", "win_loss_pct", "gb", "pts_per_g", "opp_pts_per_g", "srs"]

# Determinem el rang temporal que ens interessa, des de 1950 (quan s'estableix
# la NBA) fins a l'actualitat. 
years = [*range(1950, 1955, 1)]

def getStandings(years):
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

# Ho passem a csv:
getStandings(range(1950, 1955, 1)).to_csv("provaFuncio.csv", index=False)
