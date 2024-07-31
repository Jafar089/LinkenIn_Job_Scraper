import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_linkedin_jobs(search_query, location, num_pages):
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    for page in range(num_pages):
        url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location}&start={page * 25}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for job_card in soup.find_all('div', class_='base-card'):
            job_title = job_card.find('h3', class_='base-search-card__title').text.strip() if job_card.find('h3', class_='base-search-card__title') else None
            company = job_card.find('h4', class_='base-search-card__subtitle').text.strip() if job_card.find('h4', class_='base-search-card__subtitle') else None
            location = job_card.find('span', class_='job-search-card__location').text.strip() if job_card.find('span', class_='job-search-card__location') else None
            job_link = job_card.find('a', class_='base-card__full-link')['href'] if job_card.find('a', class_='base-card__full-link') else None

            # Get job description and company details
            if job_link:
                job_response = requests.get(job_link, headers=headers)
                job_soup = BeautifulSoup(job_response.text, 'html.parser')
                job_description = job_soup.find('div', class_='description__text').text.strip() if job_soup.find('div', class_='description__text') else None
                company_website = job_soup.find('a', class_='topcard__org-name-link')['href'] if job_soup.find('a', class_='topcard__org-name-link') else None

                jobs.append({
                    'Job Title': job_title,
                    'Company': company,
                    'Location': location,
                    'Job Description': job_description,
                    'Job Apply Link': job_link,
                    'Company Website': company_website
                })

    return jobs

def save_jobs_to_csv(jobs, filename):
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False)

# Streamlit app
st.title('LinkedIn Job Scraper')
st.write('Enter your search query and location to scrape job listings from LinkedIn.')

search_query = st.text_input('Search Query', 'Machine Learning Engineer')
location = st.text_input('Location', 'Punjab, Pakistan')
num_pages = st.number_input('Number of Pages to Scrape', min_value=1, max_value=10, value=1)

if st.button('Scrape Jobs'):
    with st.spinner('Scraping jobs...'):
        jobs = scrape_linkedin_jobs(search_query, location, num_pages)
        if jobs:
            save_jobs_to_csv(jobs, 'Your_Jobs.csv')
            st.success(f'Successfully scraped {len(jobs)} jobs!')
            st.write(pd.DataFrame(jobs))
            st.download_button('Download CSV', data=pd.DataFrame(jobs).to_csv(index=False), file_name='Your_Jobs.csv', mime='text/csv')
        else:
            st.error('No jobs found. Please try again with different parameters.')
