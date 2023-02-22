import concurrent.futures
import requests
from bs4 import BeautifulSoup
import csv
from AddCsv import CSVWriter
import re

class ParuVendu():
    
    def __init__(self):
        proxy_host = "192.168.126.136"
        proxy_port = 3128                   #proxy privé
        proxy_login = "defint"
        proxy_pass = "root"
        self.data = []
        self.url = 'https://www.paruvendu.fr/auto-moto/listefo/default/'
        self.proxies = {
            'https': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}",
            'http': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}"
        }
        
    def get_html(self, page):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        proxies = self.proxies
        url = f"{self.url}?p={page}"
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Une erreur s'est produite lors de la récupération du contenu : {e}")
            return None

    def scrape_page(self, page):
        html = self.get_html(page)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            data = []
            for article in soup.find_all('div', {'class': 'ergov3-annonceauto'}):
                try:
                    title = article.find('h3').text.strip()
                    price = article.find('div', {'class': 'ergov3-priceannonce-auto'}).text.strip()
                    price = re.search(r'\d[\d ]*\d', price).group(0)
                    km = article.find_all('span', {'class': 'txt-mea'})[1].text.strip()
                    km = re.search(r'\d[\d ]*\d',km).group(0)
                    data.append({'titre': title, 'prix': price, 'km': km})
                except:
                    continue
            return data
        else:
            print("Erreur: impossible de récupérer le contenu de la page")
            return []

    def scrape(self, nb_pages):
        with concurrent.futures.ThreadPoolExecutor() as executor:                           #c'est une bibliothèque que j'ai trouver pour aller beaucoup plus vite
            futures = [executor.submit(self.scrape_page, i+1) for i in range(nb_pages)]
            for future in concurrent.futures.as_completed(futures):
                data = future.result()
                self.data.extend(data)
        writer = CSVWriter('paruvendu.csv', ['titre', 'prix', 'km'])
        writer.writeCsv(self.data)
    
        
        
        
nb_pages = 50   #nombre de page à scraper
scraper = ParuVendu()
scraper.scrape(nb_pages)   