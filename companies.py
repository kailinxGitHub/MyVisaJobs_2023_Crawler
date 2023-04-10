import requests
from bs4 import BeautifulSoup
import re
from prettytable import PrettyTable
import csv

page = requests.get('https://www.myvisajobs.com/Software-Engineer-2023JT.htm')

soup = BeautifulSoup(page.text, 'html.parser')
table = soup.find('table', class_='tbl')

# Find all the <tr> tags inside the table
rows = table.find_all('tr')

name_link_dict = {}
for row in rows:
    td_tags = row.find_all('td')
    if len(td_tags) >= 2:
        name = td_tags[1].get_text().strip()
        
        # link
        first_part = 'https://www.myvisajobs.com/'
        second_part = row.find('a')['href']
        link = first_part + second_part
        name_link_dict[name] = link

#cleaning
new_dict = dict(list(name_link_dict.items())[1:])
