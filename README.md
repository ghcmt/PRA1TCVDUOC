# Tipologia i Cicle de Vida de les Dades
## Pràctica 1: Com podem capturar les dades de la web?
**Autors**: Carlos Martínez Torró (cmtorro@uoc.edu) i Xavier Roca Canals (xrocaca@uoc.edu)

En aquesta pràctica utilitzarem tècniques de _web scraping_ per a obtenir un dataset d'estadístiques històriques de la NBA i la WNBA des de la seva creació (1949 i 1997, respectivament).

## Descripció dels arxius del repositori
* En aquest repositori trobem el **dataset** generat a la carpeta homònima. Aquest és un arxiu CSV amb 1900 observacions i 53 variables (explicades a la memòria que s'adjunta). Conté dades estadístiques de tots els equips de la NBA des del 1949 fins l'actualitat i dels equips de la WNBA des de 1997 fins actualment. 
* A la carpeta _source_ trobem dos arxius: _NBAWNBAStatsScraper.py_ i _main.py_. Veiem-los per separat:
  * L'arxiu **NBAWNBAStatsScraper.py** conté una classe de Python. En aquesta classe trobem tots els mètodes que faran el _web scraping_ a partir d'una URL que es passa com a paràmetre. Els mètodes estan descrits en profunditat a la memòria PDF adjuntada.
  * **Main.py**: és el fitxer Python que s'ha d'executar per a obtenir el dataset. S'encarrega de cridar a la classe NBAWNBAStatsScraper amb el link de la pàgina que volem _scrapejar_. 
* Finalment (a banda d'aquest fitxer **README.md**), trobem l'arxiu **LICENSE.md**, que conté la llicència del nostre repositori. Hem triat la llicència Creative Common Zero (CC0). El raonament de la nostra decisió també es troba a la memòria. 

## DOI del Dataset
DOI:

URL:


