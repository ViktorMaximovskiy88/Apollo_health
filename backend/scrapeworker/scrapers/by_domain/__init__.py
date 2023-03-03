from backend.scrapeworker.scrapers.by_domain.aetna import AetnaScraper
from backend.scrapeworker.scrapers.by_domain.aultcas import AultcasScraper
from backend.scrapeworker.scrapers.by_domain.bcbsfl import BcbsflScraper
from backend.scrapeworker.scrapers.by_domain.bcbsnj import BcbsnjScraper
from backend.scrapeworker.scrapers.by_domain.formulary_navigator import FormularyNavigatorScraper
from backend.scrapeworker.scrapers.by_domain.horizonblue import HorizonBlueScraper
from backend.scrapeworker.scrapers.by_domain.humana import HumanaScraper
from backend.scrapeworker.scrapers.by_domain.par_formulary_navigator import (
    ParFormularyNavigatorScraper,
)
from backend.scrapeworker.scrapers.by_domain.univerahealthcare import UniveraHealthcareScraper
from backend.scrapeworker.scrapers.direct_download import PlaywrightBaseScraper

domain_scrapers: list[type[PlaywrightBaseScraper]] = [
    AetnaScraper,
    AultcasScraper,
    BcbsflScraper,
    BcbsnjScraper,
    FormularyNavigatorScraper,
    ParFormularyNavigatorScraper,
    HorizonBlueScraper,
    HumanaScraper,
    UniveraHealthcareScraper,
]


def select_domain_scraper(url, site: None = None):
    for scraper in domain_scrapers:
        if scraper.scrape_select(url, site):
            return scraper
    return None
