# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
import os

class NBAWNBAStatsScraper:

    def __init__(self, base_link):
        # Inicialitzem totes les variables necessàries
        # Base Link
        self.base_link = base_link 
        # NBA Base Link
        self.nba_base_link = base_link + '/leagues/'
        # WNBA Base Link
        self.wnba_base_link = base_link + '/wnba/years/'
        # User Agent
        self.headers = {'user-agent': 'PRA1_cmtorro_xrocaca'}
        # Ids de les taules sobre informació general de cada temporada
        self.standings_ids = ["divs_standings_E", "divs_standings_W", "divs_standings_",
                              "standings_e", "standings_w"]
        # Columnes de les taules anteriors
        self.standings_cols = ["wins", "losses", "win_loss_pct", "gb", "pts_per_g", "opp_pts_per_g"]
        # Id de la taula sobre els partits de cada temporada
        self.per_game_id = 'per_game-team'
        # Columnes de la taula anterior
        self.per_game_cols = ['g', 'mp', 'fg', 'fga', 'fg_pct', 'fg3', 
                              'fg3a', 'fg3_pct', 'fg2', 'fg2a', 'fg2_pct', 
                              'ft', 'fta', 'ft_pct', 'orb', 'drb', 'trb',
                              'ast', 'stl', 'blk', 'tov', 'pf', 'pts']
        # Id de la taula avancada sobre els partits de cada temporada
        self.advanced_ids = 'advanced-team'
        # Columnes de la taula anterior
        self.advanced_cols = ['age', 'wins', 'losses', 'wins_pyth', 
                              'losses_pyth', 'mov', 'sos', 'srs', 
                              'off_rtg', 'def_rtg', 'net_rtg', 'pace', 
                              'fta_per_fga_pct', 'fg3a_per_fga_pct', 
                              'ts_pct', 'efg_pct', 'tov_pct', 'orb_pct', 
                              'ft_rate', 'opp_efg_pct', 'opp_tov_pct', 
                              'drb_pct', 'opp_ft_rate']


    def get_all_links(self, base_link, league_links):

        all_links = []

        for league_link in league_links:
            page = requests.get(league_link)
            soup = BeautifulSoup(page.text, 'html.parser')

            if('wnba' in league_link):
                table_content = soup.find_all('table', {'id': 'yearlist'})
            else:
                table_content = soup.find_all('table', {'id': 'stats'})
        
            seasons_links = []
            seasons = []

            # Mirem cada fila per tal d'obtenir els links de cada temporada conjuntament amb l'any de la temporada
            for row in table_content[0].find_all('tr')[3:]:

                try:
                    if('wnba' in league_link):
                        seasons_links.append(base_link + row.find('a', href=True)['href'])
                        seasons.append(row.find('th', {'data-stat' : 'year_id'}).text)
                    else:
                        if('NBA' in row.find('td', {'data-stat' : 'lg_id'}).text):
                            seasons_links.append(base_link + row.find('a', href=True)['href'])
                            seasons.append(row.find('th', {'data-stat' : 'season'}).text)

                except AttributeError:
                    continue

            all_links.append([seasons_links, seasons])

        return all_links


    def get_standings(self, soup, year, ids, cols):
        # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
        stats = []
        
        # Busquem el títol de l'objecte BeautifulSoup per determinar la lliga:
        title = str(soup.find('title'))
            
        # Agafem les taules que ens interessen: conferència est i oest.
        tables = []
        for tableId in ids:
            table = soup.find(name = "table", attrs = {"id" : tableId})
            tables.append(table)
            
        for table in tables:
            # Aquest Try-Catch està pensat per si és una temporada antiga i no
            # hi ha conferències i, per tant, no existeix aquesta taula i no
            # trobaríem cap 'tr'. Per això, fem continue per anar a la següent taula:
            if table is not None:
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
                        team['Season'] = year
                        if "WNBA" in title:
                            team['League'] = "WNBA"
                        else:
                            team['League'] = "NBA"
                        team['Team'] = row.find('th', {'data-stat' : 'team_name'}).text
                        for col in cols:
                            team[col] = row.find('td', {'data-stat' : col}).text
                        team['Playoffs'] = "Yes" if "*" in team['Team'] else "No"
                    except AttributeError:
                        continue 
                    
                    # Annexem les dades a la llista que hem creat prèviament:
                    stats.append(team)

        # Generem el dataframe amb les estadístiques que hem recollit:
        standings = pd.DataFrame(stats)
        
        # Traiem l'asterisc que indica classificació a playoffs del nom de l'equip,
        # ja que ja tenim una columna que ho referencia. 
        standings['Team'] = standings['Team'].map(lambda x: x.rstrip('*'))
        return standings

    def get_per_game_stats(self, soup, year, ids, cols):       
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
                team['Season'] = year
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

    def get_advanced_stats(self, soup, year, ids, cols): 
        # Creem una llista on guardarem les estadístiques de la taula per cada temporada:
        advStats = []  
            
        # Busquem la taula a partir de la id:
        advTable = soup.find_all('table', {'id': ids})
        
        # Iterem per les files i de nou no guardem l'última fila:
        for row in advTable[0].find_all('tr')[:-1]:    
            team = {}
            try:
                team['Season'] = year
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


    def get_all_stats(self, season_links, seasons):

        # Creem les llistes on guardarem les dades de cada temporada:
        stlist = []
        pGlist = []
        advlist = []        

        for link, season in zip(season_links, seasons):

            print(f"Scraping link {link}")

            response = requests.get(link, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            title = str(soup.find("title"))
            if not "Page Not Found" in title:
                # Cridem a les funcions i comencem agafant les dades de les
                # classificacions:
                standings = self.get_standings(soup, season, self.standings_ids, self.standings_cols)
                stlist.append(standings)
                
                # Agafem les dades per partit de cada equip:
                pG = self.get_per_game_stats(soup, season, self.per_game_id, self.per_game_cols)
                pGlist.append(pG)
                    
                # Finalment, recollim les mètriques avançades:
                adv = self.get_advanced_stats(soup, season, self.advanced_ids, self.advanced_cols)
                advlist.append(adv)
                    
                # Deixem descansar al servidor entre temporada i temporada:
                sleep(randint(5, 10))

        # Generem els dataframes amb les dades de les temporades desitjades:
        df1 = pd.concat(stlist)
        df2 = pd.concat(pGlist)
        df3 = pd.concat(advlist)
        
        # Unim els dataframes a partir de les variables comunes:
        finalDF = df1.merge(df3, on= ['Season', 'Team', 'wins', 'losses']).merge(df2, on = ['Season', 'Team'])

        return finalDF


    def NBA_WNBA_scraper(self):
        
        # Obtenim tots els links de les pàgines a fer web scraping
        all_links = self.get_all_links(self.base_link, [self.nba_base_link, self.wnba_base_link])
        
        all_df = []
        # Generem els dataframes a partir de cada temporada dividides en les dues lligues (NBA/WNBA)
        for links in all_links:
            all_df.append(self.get_all_stats(links[0], links[1]))

        finalDF = pd.concat(all_df)

        

        # Exportem les dades a csv i les guardem en una nova carpeta:
        csvFolder = os.path.join(os.getcwd().replace("/source", ""), r'dataset')
        if not os.path.exists(csvFolder):
            os.makedirs(csvFolder)

        # Creem el dataset final
        finalDF.to_csv(csvFolder+"/dataset.csv", index = False) 
