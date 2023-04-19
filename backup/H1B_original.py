import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def get_university_data():
    # Getting the links
    page = requests.get('https://www.myvisajobs.com/Software-Engineer-2023JT.htm')
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find('table', class_='tbl')
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
    # Cleaning
    new_dict = dict(list(name_link_dict.items())[1:])

    data = []
    for name, link in new_dict.items():
        page = requests.get(link)
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
            name_pattern = re.compile(r"[a-zA-Z\s]+") # todo fix symbols being cut out
            uni_name = name_pattern.search(item).group()
            number_pattern = re.compile(r"\d+")
            number = number_pattern.search(item).group()
            organized_list[uni_name] = number

        for uni_name, number in organized_list.items():
            data.append([name, uni_name, int(number)])

    return pd.DataFrame(data, columns=['Company', 'University', 'Number'])

def main():
    st.set_page_config(page_title="University Recruitment Info", layout="wide")
    st.title("University Recruitment Info")

    st.header("Companies and Universities")

    university_data = get_university_data()
    st.write(university_data)

    st.header("Filter by Company")
    company_name = st.selectbox("Select a company", sorted(university_data['Company'].unique()))
    filtered_data = university_data[university_data['Company'] == company_name]
    st.write(filtered_data)


main()