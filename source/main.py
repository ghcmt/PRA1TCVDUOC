from NBAWNBAStatsScraper import NBAWNBAStatsScraper

if __name__ == "__main__":
    
    base_link = "https://www.basketball-reference.com"
    stats_scraper = NBAWNBAStatsScraper(base_link)
    stats_scraper.NBA_WNBA_scraper()