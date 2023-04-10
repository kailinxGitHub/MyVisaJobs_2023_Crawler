import requests
from bs4 import BeautifulSoup
import re
from prettytable import PrettyTable
import csv

page = requests.get('https://www.myvisajobs.com/Visa-Sponsor/Microsoft/356252.htm')

soup = BeautifulSoup(page.text, 'html.parser')
td_tags = soup.find_all('td')

## Code for parsing university for every company
# Finding the keyword
combined_list = []
for td in td_tags:
    td_list = [i for i in td]
    combined_list.extend(td_list)
for indexposition in combined_list:
    if "College:" == indexposition:
        i_index = combined_list.index(indexposition)
        found_item = combined_list[i_index+1]

# Mapping the items
mapped_found_item = list(map(str, found_item.split(";")))
organized_list = {}
for item in mapped_found_item:
    letters_to_remove = "()"
    for letter in letters_to_remove:
        item = item.replace(letter, "")
    name_pattern = re.compile(r"[a-zA-Z\s]+")
    name = name_pattern.search(item).group()
    number_pattern = re.compile(r"\d+")
    number = number_pattern.search(item).group()
    organized_list[name] = number


# Table
table = PrettyTable()
title = soup.title.string
title_truncated = title.split(',')[0]
words = re.findall(r'\w+', title_truncated)
title = ' '.join(words)
print(title)

for name, number in organized_list.items():
    table.add_row([name, number])

# CSV
table_data = [(key, value) for key, value in organized_list.items()]
with open('table.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([title])
    writer.writerow(['Name', 'Number'])
    writer.writerows(table_data)