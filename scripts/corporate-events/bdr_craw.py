import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def extract_and_persist_corporate_events(cvm_code):
    url = f'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/ResumoEventosCorporativos.aspx?codigoCvm={cvm_code}&tab=3&idioma=pt-br'
    tables = pd.read_html(url)
    print(f'TABLES FOUND: {len(tables)}')
    counter = 0
    for table in tables:
        print(f'Saving csv: b3data/{cvm_code}-{counter}')
        table.to_csv(f'bdrdata/{cvm_code}-{counter}.csv')
        counter = counter + 1

url = 'http://bvmf.bmfbovespa.com.br/cias-listadas/Mercado-Internacional/Mercado-Internacional.aspx?Idioma=pt-br'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table')

links = []

for tr in table.findAll("tr"):
    trs = tr.findAll("td")
    record = []
    for each in trs:
        try:
            link = each.find('a')['href']
            links.append(link)
            record.append(link)
        except:
            pass


for link in links:
    m = re.search('codigoCvm=(.+?)&', link)
    if m:
        cvm_code = m.group(1)
        print(f'processing cvm_code = {cvm_code}')
        extract_and_persist_corporate_events(cvm_code)