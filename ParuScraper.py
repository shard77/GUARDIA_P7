import concurrent.futures
import requests
from bs4 import BeautifulSoup
from AddCsv import CSVWriter
import re
import time
import argparse


class ParuScraper():
    def __init__(self):
        self.data = []
        self.url = 'https://www.paruvendu.fr/'

    def get_html(self, category):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        url = self.url+category

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Une erreur s'est produite lors de la récupération du contenu : {e}")
            return None

    def voitures_scraper(self, category):
        html = self.get_html(category)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            data = []
            for article in soup.find_all('div', {'class': 'ergov3-annonceauto'}):
                try:
                    title = article.find('h3').text.strip()
                    price = article.find('div', {'class': 'ergov3-priceannonce-auto'}).text.strip()
                    price = re.search(r'\d[\d ]*\d', price).group(0)
                    desc = article.find('cite', {'class': 'texte'}).text.strip()
                    url = article.find('a')['href']
                    data.append({'titre': title, 'prix': price, 'description': desc, 'url': url})
                except (AttributeError, TypeError):
                    continue
            return data
        else:
            print("Erreur: impossible de récupérer le contenu de la catégorie")
            return []

    def annonces_scraper(self, category):
        html = self.get_html(category)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            data = []
            for article in soup.find_all('div', {'class': 'debarras-annonce'}):
                try:
                    title = article.find('p', {'class': 'titleann'}).text.strip()
                    title = title.splitlines()[0]
                    price = article.find('div', {'class': 'debarras-priceannonce'}).text.strip().replace('€', '')
                    price = price.splitlines()[0]
                    desc = article.find('p', {'class': None}).text.strip()
                    url = article.find('a', {'class': 'globann'})['href']
                    data.append({'titre': title, 'prix': price, 'description': desc, 'url': url})
                except (AttributeError, TypeError):
                    continue
            return data
        else:
            print("Erreur: impossible de récupérer le contenu de la page Annonces")
            return []

    def scrape(self, nb_pages, category):
        category = category.replace(self.url, '')
        category_name = category.split('/')[0]
        items_scraped = 0

        if "mondebarras/" in category:
            print(f'Scraping de la catégorie "{category_name}" en cours...')
            scraped_page = self.annonces_scraper
            format_nav = '?p'
        elif "auto-moto/" in category:
            print(f'Scraping de la catégorie "{category_name}" en cours...')
            scraped_page = self.voitures_scraper
            format_nav = '&p'
        else:
            print("Catégorie non prise en charge.")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(scraped_page, category + f'{format_nav}={i+1}') for i in range(nb_pages)]
            for future in concurrent.futures.as_completed(futures):
                data = future.result()
                items_scraped += len(data)
                self.data.extend(data)

        match category_name:
            case "auto-moto":
                writer = CSVWriter(f'auto-moto_{time.time()}.csv', ['titre', 'prix', 'description', 'url'])
                writer.write_csv(self.data)
            case "mondebarras":
                writer = CSVWriter(f'debarras_{time.time()}.csv', ['titre', 'prix', 'description', 'url'])
                writer.write_csv(self.data)

        print(f'Scraping de la catégorie "{category_name}" terminé!')
        print(f'{items_scraped} annonces ont été récupérées.')


parser = argparse.ArgumentParser(description='Scrape les annonces de ParuVendu.fr')
parser.add_argument("-u", help="URL de la catégorie à scraper")
parser.add_argument("-p", help="Nombre de pages à scraper")
args = parser.parse_args()
args = vars(args)

if args['u'] and args['p']:
    instance = ParuScraper()
    instance.scrape(int(args['p']), args['u'])
else:
    category_url = input("Entrez l'url de la catégorie à scraper:\n")
    num_pages = int(input("Combien de pages voulez-vous scraper ?\n"))
    instance = ParuScraper()
    instance.scrape(num_pages, category_url)

