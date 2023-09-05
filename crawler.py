import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import csv
import datetime
import pandas as pd
from datetime import datetime


class Country:
   def __init__(self, name, capital, currency, population):
    self.name = name
    self.capital = capital
    self.currency = currency
    self.population = population
    self.timestamp = None  # Adicione um atributo timestamp


def getLinkAndNames(page):
    for a in page.find("table").find_all('a'):
      country_links.append(a.attrs['href'])

def populateCountryLinks(page_link):
   index = urlopen(base_url + page_link)
   bs_index = BeautifulSoup(index.read(), 'html.parser')
   getLinkAndNames(bs_index)
   next_page = bs_index.find('a', string = re.compile('^Next.'))
   if next_page == None:
      return
   populateCountryLinks(next_page['href'])

def getRowInformation(page, field):
   elementsThatMatchWithRow = page.find('tr', id="places_"+field+"__row")
   return elementsThatMatchWithRow.findChild('td', {"class": "w2p_fw"}).text.strip()
   
def getCountry(page_url):
   index = urlopen(base_url + page_url)
   page = BeautifulSoup(index.read(), 'html.parser')
   name = getRowInformation(page, "country")
   capital = getRowInformation(page, "capital")
   currency = getRowInformation(page, "currency_name")
   population = getRowInformation(page, "population")
   return Country(name, capital, currency, population)

base_url = 'http://127.0.0.1:8000'

country_links = []
countries = []

index = urlopen(base_url + '/places/default/index')
bs_index = BeautifulSoup(index.read(), 'html.parser')
next_page = bs_index.find('a', string = re.compile('^Next.'))
populateCountryLinks(next_page['href'])

for link in country_links:
   countries.append(getCountry(link))

csv_filename = "countries.csv"

csv_filename = "countries.csv"
if os.path.exists(csv_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_csv_filename = f"countries_{timestamp}.csv"
else:
    new_csv_filename = csv_filename

data_dict = []
for country in countries:
    country_data = {
        "name": country.name,
        "capital": country.capital,
        "currency": country.currency,
        "population": country.population,
        "timestamp": datetime.now()
    }
    data_dict.append(country_data)

df = pd.DataFrame(data_dict)

if os.path.exists(csv_filename):
    print('found the file')
    old_df = pd.read_csv(csv_filename)

    for index, row in df.iterrows():
        country_name = row['name']
        old_row = old_df.loc[old_df['name'] == country_name]
        if not old_row.empty:
            for col in df.columns:
                if col != 'name' and row[col] != old_row[col].values[0]:
                    old_df.loc[old_df['name'] == country_name, col] = row[col]
                    old_df.loc[old_df['name'] == country_name, 'timestamp'] = row['timestamp']

    old_df.to_csv(csv_filename, index=False)
else:
    df.to_csv(new_csv_filename, index=False)

print("CSV updated succesfully.")