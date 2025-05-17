import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def cleaning_green_card_applicant_profile(category_raw_list):
    if isinstance(category_raw_list, str):
        list_in_category = list(map(str, category_raw_list.split(";")))
    else:
        list_in_category = []
        
    data = []
    # Mapping the items
    organized_list = {}
    for item in list_in_category:
        letters_to_remove = "()"
        for letter in letters_to_remove:
            item = item.replace(letter, "")
        name_pattern = re.compile(r"[a-zA-Z\s]+")
        cat_items = name_pattern.search(item)
        if cat_items:
            cat_items_name = cat_items.group().strip()
            cat_items_name = re.sub(' +', ' ', cat_items_name)
        else:
            continue
        number_pattern = re.compile(r"\d+")
        number_match = number_pattern.search(item)
        if number_match:
            number = number_match.group()
        else:
            continue
        
        #temp
        name = "Amazon,Com Services"
        data.append([name, cat_items_name, int(number)])
    print(pd.DataFrame(data, columns=['Company', 'University', 'Number']))

page_url = "https://www.myvisajobs.com/Visa-Sponsor/Amazon-Com-Services/1352502.htm"
page = requests.get(page_url)
soup = BeautifulSoup(page.text, 'html.parser')
td_tags = soup.find_all('td')

combined_list = []
for td in td_tags:
    td_list = [i for i in td]
    combined_list.extend(td_list)

# college filtering
found_items_college = ""
for indexposition in combined_list:
    if "College:" == indexposition:
        i_index = combined_list.index(indexposition)
        found_items_college = combined_list[i_index+1]
