import requests
from bs4 import BeautifulSoup
import re

page = requests.get('https://www.myvisajobs.com/Visa-Sponsor/Microsoft/356252.htm')

# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')

td_tags = soup.find_all('td')

combined_list = []

for td in td_tags:
    td_list = [i for i in td]
    combined_list.extend(td_list)

for indexposition in combined_list:
    if "College:" == indexposition:
        i_index = combined_list.index(indexposition)
        found_item = combined_list[i_index+1]

mapped_found_item = list(map(str, found_item.split(";")))
organized_list = {}
for item in mapped_found_item:
    letters_to_remove = "()"
    for letter in letters_to_remove:
        item = item.replace(letter, "")
    # Name
    name_pattern = re.compile(r"[a-zA-Z\s]+")
    name = name_pattern.search(item).group()

    # Number
    number_pattern = re.compile(r"\d+")
    number = number_pattern.search(item).group()

    organized_list[name] = number

from prettytable import PrettyTable
# create a table with two columns
table = PrettyTable()
table.field_names = ["Name", "Number"]

# add data to the table
for name, number in organized_list.items():
    table.add_row([name, number])

import csv

# create a list of tuples from the dictionary
table_data = [(key, value) for key, value in organized_list.items()]

# write the table to a CSV file
with open('table.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', 'Number'])  # write header row
    writer.writerows(table_data)  # write the data

