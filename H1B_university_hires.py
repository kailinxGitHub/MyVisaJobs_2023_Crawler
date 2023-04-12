import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import shutil
import re
import csv
import os

def save_company_data_to_csv(name, organized_list):
    if not os.path.exists('csv'):
        os.makedirs('csv')
    
    valid_name = ''.join(char for char in name if char.isalnum())
    csv_name = f"csv/{valid_name}.csv"
    
    table_data = [(key, value) for key, value in organized_list.items()]
    with open(csv_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name])
        writer.writerow(['Name', 'Number'])
        writer.writerows(table_data)

def load_all_company_data():
    data = []
    
    for filename in os.listdir('csv'):
        if filename.endswith('.csv'):
            with open(f'csv/{filename}', newline='') as csvfile:
                reader = csv.reader(csvfile)
                company_name = next(reader)[0]
                next(reader)
                for row in reader:
                    university, number = row
                    data.append([company_name, university, int(number)])
    
    return pd.DataFrame(data, columns=['Company', 'University', 'Number'])

def get_university_data():
    # Check if the CSV folder already exists and has files, and load the data from the files.
    if os.path.exists('csv') and len(os.listdir('csv')) > 0:
        return load_all_company_data()

    # If the CSV folder does not exist or is empty, scrape the data and save it to the files.
    # page = requests.get('https://www.myvisajobs.com/Software-Engineer-2023JT.htm')
    # soup = BeautifulSoup(page.text, 'html.parser')
    # table = soup.find('table', class_='tbl')
    # rows = table.find_all('tr')
    # name_link_dict = {}
    # for row in rows:
    #     td_tags = row.find_all('td')
    #     if len(td_tags) >= 2:
    #         name = td_tags[1].get_text().strip()
    #         # link
    #         first_part = 'https://www.myvisajobs.com/'
    #         second_part = row.find('a')['href']
    #         link = first_part + second_part
    #         name_link_dict[name] = link
    
    base_url = 'https://www.myvisajobs.com/Software-Engineer'
    url_suffix = '-2023JT.htm'
    name_link_dict = {}

# Loop through the desired number of pages (1 to 4 in this case)
    for page_number in range(1, 5):
        # Generate the URL for the current page
        if page_number == 1:
            page_url = f'{base_url}{url_suffix}'
        else:
            page_url = f'{base_url}_{page_number}{url_suffix}'

        # Scrape the current page
        page = requests.get(page_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('table', class_='tbl')
        rows = table.find_all('tr')

        # Extract the company names and links from the current page
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

                    # Save the company's data to a CSV file.
        save_company_data_to_csv(name, organized_list)

        # Add the company's data to the main data list.
        for uni_name, number in organized_list.items():
            data.append([name, uni_name, int(number)])

    # Save the data to CSV files and return the data as a pandas DataFrame.
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

    st.header("Filter by University")
    university_name = st.selectbox("Select a university", sorted(university_data['University'].unique()))
    filtered_data_by_university = university_data[university_data['University'] == university_name]
    st.write(filtered_data_by_university)

    st.header("Reset Data")
    reset_button = st.button("Reset")

    if reset_button:
        csv_folder = 'csv'
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                os.remove(f'{csv_folder}/{filename}')
        st.success("All CSV files have been cleared.")


main()
