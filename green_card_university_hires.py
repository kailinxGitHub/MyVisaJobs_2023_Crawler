import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import csv
import os

def save_company_data_to_csv(name, organized_list):
    if not organized_list:
        return

    # if csv does not exist
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

def get_university_data(options):
    # Check if the CSV folder already exists and has files, and load the data from the files.
    if os.path.exists('csv') and any(file.endswith('.csv') for file in os.listdir('csv')):
        return load_all_company_data()
    
    base_url_h1b = "https://www.myvisajobs.com/Software-Engineer"
    url_suffix_h1b = "-2023JT.htm"

    base_url_gc = "https://www.myvisajobs.com/Reports/2023-Green-Card-Sponsor.aspx"

    pages_map = {
        "2023 H1B Visa Reports Page 1": f"{base_url_h1b}{url_suffix_h1b}",
        "2023 H1B Visa Reports Page 2": f"{base_url_h1b}_2{url_suffix_h1b}",
        "2023 H1B Visa Reports Page 3": f"{base_url_h1b}_3{url_suffix_h1b}",
        "2023 H1B Visa Reports Page 4": f"{base_url_h1b}_4{url_suffix_h1b}",
        "Top 100 Green Card Sponsors Page 1": f"{base_url_gc}",
        "Top 100 Green Card Sponsors Page 2": f"{base_url_gc}?P=2",
        "Top 100 Green Card Sponsors Page 3": f"{base_url_gc}?P=3",
        "Top 100 Green Card Sponsors Page 4": f"{base_url_gc}?P=4",
    }

    if "All" in options:
        urls_to_scrape = list(pages_map.values())
    else:
        urls_to_scrape = [pages_map[option] for option in options]
    
    for page_url in urls_to_scrape:
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
                link_element = row.find('a')
                if link_element:
                    second_part = link_element['href']
                    link = first_part + second_part
                    pages_map[name] = link
        # Cleaning

    data = []
    for name, link in pages_map.items():
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        td_tags = soup.find_all('td')

        ## Code for parsing university for every company
        # Finding the keyword
        combined_list = []
        for td in td_tags:
            td_list = [i for i in td]
            combined_list.extend(td_list)
        found_item = ""
        for indexposition in combined_list:
            if "College:" == indexposition:
                i_index = combined_list.index(indexposition)
                found_item = combined_list[i_index+1]

        if isinstance(found_item, str):
            mapped_found_item = list(map(str, found_item.split(";")))
        else:
            mapped_found_item = []

        # Mapping the items
        mapped_found_item = list(map(str, found_item.split(";")))
        organized_list = {}
        for item in mapped_found_item:
            letters_to_remove = "()"
            for letter in letters_to_remove:
                item = item.replace(letter, "")
            name_pattern = re.compile(r"[a-zA-Z\s]+")
            uni_name_match = name_pattern.search(item)
            if uni_name_match:
                uni_name = uni_name_match.group()
            else:
                continue
            number_pattern = re.compile(r"\d+")
            number_match = number_pattern.search(item)
            if number_match:
                number = number_match.group()
            else:
                continue
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
    st.subheader("Note: Reset every time after use!")
    st.subheader("Note: All of the data is based on the GREEN CARD PROFILE!")

    if 'university_data' not in st.session_state:
        st.session_state.university_data = pd.DataFrame()

    with st.sidebar.header("Reset Data"):
        reset_button = st.sidebar.button("Reset")

        options = st.sidebar.multiselect(
            "Select pages to scrape",
            [
                "All",
                "2023 H1B Visa Reports Page 1",
                "2023 H1B Visa Reports Page 2",
                "2023 H1B Visa Reports Page 3",
                "2023 H1B Visa Reports Page 4",
                "Top 100 Green Card Sponsors Page 1",
                "Top 100 Green Card Sponsors Page 2",
                "Top 100 Green Card Sponsors Page 3",
                "Top 100 Green Card Sponsors Page 4",
            ],
        )

        run_button = st.sidebar.button("Run")

    if reset_button:
        csv_folder = 'csv'
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                os.remove(f'{csv_folder}/{filename}')
        st.success("All CSV files have been cleared.")
        st.session_state.university_data = pd.DataFrame()
        options = []


    if run_button:
        st.session_state.university_data = get_university_data(options)

    if not st.session_state.university_data.empty:
        filter_company_placeholder = st
        filter_company_placeholder.header("Filter by Company")
        companies = sorted(st.session_state.university_data['Company'].unique())
        default_company = 'Amazon Web Services'  # Replace this with the actual name of the default company
        default_index = companies.index(default_company) if default_company in companies else 0
        company_name = filter_company_placeholder.selectbox("Select a company", companies, index=default_index)
        filtered_data = st.session_state.university_data[st.session_state.university_data['Company'] == company_name]
        sorted_data = filtered_data.sort_values('Number', ascending=False)  # Corrected column name
        filter_company_placeholder.write(sorted_data)

        filter_university_placeholder = st
        filter_university_placeholder.header("Filter by University")
        universities = sorted(st.session_state.university_data['University'].unique())
        default_university = 'Northeastern University'  # Replace this with the actual name of the default university
        default_index = universities.index(default_university) if default_university in universities else 0
        university_name = filter_university_placeholder.selectbox("Select a university", universities, index=default_index)
        filtered_data_by_university = st.session_state.university_data[st.session_state.university_data['University'] == university_name]
        sorted_filtered_data_by_university = filtered_data_by_university.sort_values('Number', ascending=False)  # Corrected column name
        filter_university_placeholder.write(sorted_filtered_data_by_university)

main()