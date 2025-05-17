import streamlit as st
st.set_page_config(
    page_title="University Recruitment Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8')
sns.set_theme(style="whitegrid")

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1 {
        color: #2c3e50;
        padding-bottom: 1rem;
        border-bottom: 2px solid #eee;
    }
    h2 {
        color: #34495e;
        margin-top: 2rem;
    }
    h3 {
        color: #7f8c8d;
    }
    .stSelectbox {
        background-color: transparent;
    }
    .stSelectbox > div {
        background-color: transparent !important;
    }
    .stSelectbox > div > div {
        background-color: transparent !important;
    }
    .stSelectbox > div > div > div {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

def save_company_data_to_csv(name, organized_list):
    if not organized_list:
        return

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
        try:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.text, 'html.parser')
            table = soup.find('table', class_='tbl')
            
            if table is None:
                st.warning(f"Could not find data table on page: {page_url}")
                continue
                
            rows = table.find_all('tr')

            for row in rows:
                td_tags = row.find_all('td')
                if len(td_tags) >= 2:
                    name = td_tags[1].get_text().strip()
                    first_part = 'https://www.myvisajobs.com/'
                    link_element = row.find('a')
                    if link_element:
                        second_part = link_element['href']
                        link = first_part + second_part
                        pages_map[name] = link
        except Exception as e:
            st.error(f"Error processing page {page_url}: {str(e)}")
            continue

    data = []
    for name, link in pages_map.items():
        try:
            page = requests.get(link)
            soup = BeautifulSoup(page.text, 'html.parser')
            td_tags = soup.find_all('td')

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

            organized_list = {}
            for item in mapped_found_item:
                letters_to_remove = "()"
                for letter in letters_to_remove:
                    item = item.replace(letter, "")
                name_pattern = re.compile(r"[a-zA-Z\s]+")
                uni_name_match = name_pattern.search(item)
                if uni_name_match:
                    uni_name = uni_name_match.group().strip()
                    uni_name = re.sub(' +', ' ', uni_name)
                else:
                    continue
                number_pattern = re.compile(r"\d+")
                number_match = number_pattern.search(item)
                if number_match:
                    number = number_match.group()
                else:
                    continue
                organized_list[uni_name] = number

            name = re.sub(' +', ' ', name.strip())
            save_company_data_to_csv(name, organized_list)

            for uni_name, number in organized_list.items():
                data.append([name, uni_name, int(number)])
        except Exception as e:
            st.error(f"Error processing company {name}: {str(e)}")
            continue

    if not data:
        st.error("No data was collected. Please check the URLs and try again.")
        return pd.DataFrame(columns=['Company', 'University', 'Number'])
        
    return pd.DataFrame(data, columns=['Company', 'University', 'Number'])

def plot_company_data(filtered_data, company_name):
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=filtered_data.head(10), x='Number', y='University', palette='viridis')
    
    plt.title(f'Top 10 Universities for {company_name}', fontsize=16, pad=20, color='#2c3e50')
    plt.xlabel('Number of Hires', fontsize=12, labelpad=10)
    plt.ylabel('University', fontsize=12, labelpad=10)
    
    for i, v in enumerate(filtered_data.head(10)['Number']):
        ax.text(v + 0.1, i, str(v), color='#2c3e50', fontweight='bold')
    
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    sns.despine()
    plt.tight_layout()
    return plt

def plot_university_data(filtered_data, university_name):
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=filtered_data.head(10), x='Number', y='Company', palette='viridis')
    
    plt.title(f'Top 10 Companies for {university_name}', fontsize=16, pad=20, color='#2c3e50')
    plt.xlabel('Number of Hires', fontsize=12, labelpad=10)
    plt.ylabel('Company', fontsize=12, labelpad=10)
    
    for i, v in enumerate(filtered_data.head(10)['Number']):
        ax.text(v + 0.1, i, str(v), color='#2c3e50', fontweight='bold')
    
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    sns.despine()
    plt.tight_layout()
    return plt

def main():
    st.markdown("<h1 style='text-align: center;'>🎓 University Recruitment Analytics</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 Note: Reset data after each use to ensure fresh analysis")
    with col2:
        st.info("📊 Data based on Green Card profiles from myvisajobs.com")

    if 'university_data' not in st.session_state:
        st.session_state.university_data = pd.DataFrame()

    with st.sidebar:
        st.markdown("### 🛠️ Controls")
        st.markdown("---")
        
        reset_button = st.button("🔄 Reset Data", use_container_width=True)
        
        st.markdown("### 📑 Data Selection")
        options = st.multiselect(
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
        
        run_button = st.button("▶️ Run Analysis", use_container_width=True)

    if reset_button:
        csv_folder = 'csv'
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                os.remove(f'{csv_folder}/{filename}')
        st.success("✅ All data has been cleared successfully!")
        st.session_state.university_data = pd.DataFrame()
        options = []

    if run_button:
        with st.spinner('🔄 Fetching and analyzing data...'):
            st.session_state.university_data = get_university_data(options)
        st.success('✅ Data analysis complete!')

    if not st.session_state.university_data.empty:
        st.markdown("## 🏢 Company Analysis")
        companies = sorted(st.session_state.university_data['Company'].unique())
        default_company = 'Amazon Web Services'
        default_index = companies.index(default_company) if default_company in companies else 0
        
        col1, col2 = st.columns([2, 1])
        with col1:
            company_name = st.selectbox("Select a company to analyze", companies, index=default_index)
        
        filtered_data = st.session_state.university_data[st.session_state.university_data['Company'] == company_name]
        sorted_data = filtered_data.sort_values('Number', ascending=False)
        
        tab1, tab2 = st.tabs(["📊 Visualization", "📋 Data Table"])
        
        with tab1:
            st.markdown("### Top 10 Universities")
            fig = plot_company_data(sorted_data, company_name)
            st.pyplot(fig)
            plt.close()
        
        with tab2:
            st.markdown("### Detailed Hiring Data")
            st.dataframe(sorted_data, use_container_width=True)

        st.markdown("---")

        st.markdown("## 🎓 University Analysis")
        universities = sorted(st.session_state.university_data['University'].unique())
        default_university = 'Northeastern University'
        default_index = universities.index(default_university) if default_university in universities else 0
        
        col1, col2 = st.columns([2, 1])
        with col1:
            university_name = st.selectbox("Select a university to analyze", universities, index=default_index)
        
        filtered_data_by_university = st.session_state.university_data[st.session_state.university_data['University'] == university_name]
        sorted_filtered_data_by_university = filtered_data_by_university.sort_values('Number', ascending=False)
        
        tab1, tab2 = st.tabs(["📊 Visualization", "📋 Data Table"])
        
        with tab1:
            st.markdown("### Top 10 Companies")
            fig = plot_university_data(sorted_filtered_data_by_university, university_name)
            st.pyplot(fig)
            plt.close()
        
        with tab2:
            st.markdown("### Detailed Hiring Data")
            st.dataframe(sorted_filtered_data_by_university, use_container_width=True)

main()