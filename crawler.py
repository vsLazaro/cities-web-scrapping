from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

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


base_url = 'http://127.0.0.1:8000'

country_names = []
country_links = []

index = urlopen(base_url + '/places/default/index')
bs_index = BeautifulSoup(index.read(), 'html.parser')
next_page = bs_index.find('a', string = re.compile('^Next.'))
populateCountryLinks(next_page['href'])

print(country_links)

