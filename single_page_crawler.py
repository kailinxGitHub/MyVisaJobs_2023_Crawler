import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Program Info
# st.title("Green Card Profile for Amazon,Com Services")

# Functions Library
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

# Finding the key content init
page_url = "https://www.myvisajobs.com/Visa-Sponsor/Amazon-Com-Services/1352502.htm"
page = requests.get(page_url)
soup = BeautifulSoup(page.text, 'html.parser')
td_tags = soup.find_all('td')

## Code for parsing university for every company
# Finding the keyword
combined_list = []
for td in td_tags:
    td_list = [i for i in td]
    combined_list.extend(td_list)

#colleges
found_items_college = ""
for indexposition in combined_list:
    if "College:" == indexposition:
        i_index = combined_list.index(indexposition)
        found_items_college = combined_list[i_index+1]













# def cleaning_green_card_applicant_profile(text):
#     if isinstance(text, str):
#         text = list(map(str, text.split(";")))
#     else:
#         text = []

#     # Mapping the items
#     organized_list = {}
#     for item in text:
#         letters_to_remove = "()"
#         for letter in letters_to_remove:
#             item = item.replace(letter, "")
#         name_pattern = re.compile(r"[a-zA-Z\s]+")
#         uni_name_match = name_pattern.search(item)
#         if uni_name_match:
#             uni_name = uni_name_match.group().strip()  # strip leading and trailing spaces
#             uni_name = re.sub(' +', ' ', uni_name)  # replace multiple spaces with a single space
#         else:
#             continue
#         number_pattern = re.compile(r"\d+")
#         number_match = number_pattern.search(item)
#         if number_match:
#             number = number_match.group()
#         else:
#             continue
#         organized_list[uni_name] = number

#         # cleaning company name
#         name = re.sub(' +', ' ', name.strip())
#         print(name)

#       # Save the company's data to a CSV file.
        # save_company_data_to_csv(name, organized_list)

        # # Add the company's data to the main data list.
        # for uni_name, number in organized_list.items():
        #     data.append([name, uni_name, int(number)])

# # Save the data to CSV files and return the data as a pandas DataFrame.
# print(pd.DataFrame(data, columns=['Company', 'University', 'Number']))