import requests
from bs4 import BeautifulSoup
import re
import csv
import bs4


def get_conference_data(soup, conference):

    if(conference == 'Eastern'):
        id = 'confs_standings_E'

    elif(conference == 'Western'):
        id = 'confs_standings_W'

    else:
        return "Error (Bad Conference)"

    table_content = soup.find_all('table', {'id': id})

    rows = table_content[0].find_all('tr')

    # Eliminem el header de la taula
    rows.pop(0)

    # Llista amb totes les dades dels equips
    all_teams = []

    # Recorrem cada fila per agafar les seguents dades -> Nom de l'equip, W i L
    for team in rows:
        team_data = []
        team_data.append(conference)

        for element2 in team:
            if(type(element2.contents[0]) is not bs4.NavigableString):
                team_data.append(element2.contents[0].contents[0])

            else:
                team_data.append(element2.contents[0])

            if(len(team_data) >= 4):
                break

        all_teams.append(team_data)
    return all_teams

def get_per_game_stats(soup):
    table_content = soup.find_all('table', {'id': 'per_game-team'})

    rows = table_content[0].find_all('tr')

    # Eliminem el header de la taula
    rows.pop(0)
    # Eliminem el league average
    rows.pop(-1)

    # Llista amb totes les dades dels equips
    all_teams = []

    # Recorrem cada fila per agafar les seguents dades -> Nom de l'equip, W i L
    for team in rows:
        team_data = []

        for element2 in team:
            if(type(element2.contents[0]) is not bs4.NavigableString):
                team_data.append(element2.contents[0].contents[0])

            else:
                team_data.append(element2.contents[0])

        team_data.pop(0)
        all_teams.append(team_data)
    return all_teams
    

def merge_data(season_data, conference_data, per_game_stats_data):

    for per_game_team_stats in per_game_stats_data:
        for conference_team in conference_data:

            # Mirem els equips per tal de juntar dades
            if(conference_team[1] in per_game_team_stats):

                per_game_team_stats.insert(0, season_data[0])
                per_game_team_stats.insert(1, season_data[1])
                per_game_team_stats.insert(2, conference_team[0])
                per_game_team_stats.insert(5, conference_team[2])
                per_game_team_stats.insert(6, conference_team[3])

    return per_game_stats_data


def get_nba_aba_league_data(base_link):

    page = requests.get(base_link + '/leagues/')
    soup = BeautifulSoup(page.text, 'html.parser')

    table_content = soup.find_all('table', {'id': 'stats'})

    rows = table_content[0].find_all('tr')

    # Descartem headers
    rows.pop(0)
    rows.pop(0)

    # Descartem temporada actual
    rows.pop(0)

    # Llista per guardar tota la informacio general de les temporades
    all_seasons = []

    # Llista amb els enllacos de les temporades
    seasons_links = []

    # Llista amb la informacio necessaria per els enllacos de les temporades (Conte l'any i la lliga)
    seasons_info = []

    for season in rows:
        
        # Llista per agafar les dades d'una sola temporada
        season_data = []
        for element in season:

            if(element.contents):

                # Obtenim el link per entrar a cada temporada
                link = element.contents[0].get('href')

                if('leagues' in link):
                    if(base_link+link not in seasons_links):
                        seasons_links.append(base_link + link)

                season_data.append(element.contents[0].contents[0])

            else:
                season_data.append("None")

        seasons_info.append([season_data[0], season_data[1]])
        all_seasons.append(season_data)

    # Guardem en CSV una part de les dades (Primer dataset)
    f = csv.writer(open('overallinfo.csv', 'w'))
    f.writerow(["Season", "League", "Champion", "MVP", "RoY", "Points", "Rebounds", "Assists", "Win Shares"])

    for season in all_seasons:
        f.writerow(season)

    return [seasons_links, seasons_info]



if __name__ == "__main__":

    base_link = 'https://www.basketball-reference.com'
    seasons_links, season_info = get_nba_aba_league_data(base_link)


    f2 = csv.writer(open('seasonsdata.csv', 'w'))
    f2.writerow(["Season", "League", "Conference", "Team", "Games", "W", "L",
                "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "FT",
                "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"])

    for link, season_info in zip(seasons_links, season_info):

        page = requests.get(link)

        soup = BeautifulSoup(page.text, 'html.parser')

        eastern_data = get_conference_data(soup, "Eastern")
        western_data = get_conference_data(soup, "Western")

        conference_data = eastern_data + western_data

        per_game_data = get_per_game_stats(soup)

        
        data = merge_data(season_info, conference_data, per_game_data)

        for row in data:
            f2.writerow(row)
>>>>>>> e27a14ae09ecdce102a8a52f12e6afccbd7f4bfd
