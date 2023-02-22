
#Acutellement disponible pour les annonces auto(auto-moto) et les annonces classiques(Mon débarras)

import concurrent.futures
import requests
from bs4 import BeautifulSoup
from AddCsv import CSVWriter
import re

class ParuVenduScraper():

    def __init__(self):
        proxy_host = "192.168.126.136"
        proxy_port = 3128                   #proxy privé
        proxy_login = "defint"
        proxy_pass = "root"
        self.data = []
        self.url = 'https://www.paruvendu.fr/'
        self.proxies = {
            'https': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}",
            'http': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}"
        }

     
    def get_html(self, category):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        proxies = self.proxies
        url = self.url+category
        try:
            response = requests.get(url, headers=headers,proxies=proxies)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Une erreur s'est produite lors de la récupération du contenu : {e}")
            return None

    def scrap_page_voiture(self, category):
        html = self.get_html(category)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            data = []
            for article in soup.find_all('div', {'class': 'ergov3-annonceauto'}):
                try:
                    title = article.find('h3').text.strip()
                    price = article.find('div', {'class': 'ergov3-priceannonce-auto'}).text.strip()
                    price = re.search(r'\d[\d ]*\d', price).group(0)
                    desc= article.find('cite', {'class': 'texte'}).text.strip()
                    data.append({'titre': title, 'prix': price, 'description': desc})
                except:
                    continue
            return data
        else:
            print("Erreur: impossible de récupérer le contenu de la page Voiture")
            return []


    def scrap_page_annonces(self, category):
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
                    desc= article.find('p', {'class': None}).text.strip()
                    data.append({'titre': title, 'prix': price, 'description': desc})
                except:
                    continue
            return data
        else:
            print("Erreur: impossible de récupérer le contenu de la page Annonces")
            return []


    def scrape(self, nb_pages, category):
        
        if 'annonces/' in category:
            scrap_page = self.scrap_page_annonces
            format_nav= '?p'
        elif 'auto-moto/' in category:
            scrap_page = self.scrap_page_voiture
            format_nav= '&p'
        else:
            print("Catégorie non prise en charge.")
            return
        with concurrent.futures.ThreadPoolExecutor() as executor:                         
            futures = [executor.submit(scrap_page, category + f'{format_nav}={i+1}') for i in range(nb_pages)]
            for future in concurrent.futures.as_completed(futures):
                data = future.result()
                self.data.extend(data)
        writer = CSVWriter('paruvendu.csv', ['titre', 'prix', 'description'])
        writer.writeCsv(self.data)




nb_pages = 1   #nombre de page à scraper

#Copier tout ce qu'il y a après l'url de défaut et après le '/'
category = 'auto-moto/listefo/default/default?reaf=1&r=VCA00000&px1=&codeINSEE=&lo=&pa=&ray=15&ty=&a0=&km1=&fulltext='  
scraper = ParuVenduScraper()
scraper.scrape(nb_pages, category)
