from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os
import requests

def download_pdf(url):
    # Setup webdriver
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)
    driver.get(url)

    # Get the last part of the url to use as folder name
    folder_name = url.split('/')[-1]
    folder_path = os.path.join(os.path.expanduser('~/Downloads/'), folder_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Find all links with .pdf extension
    elements = driver.find_elements(By.XPATH, '//a[contains(@href, ".pdf")]')

    for element in elements:
        pdf_url = element.get_attribute('href')
        file_name = os.path.join(folder_path, pdf_url.split('/')[-1])

        # Download the file
        response = requests.get(pdf_url)
        with open(file_name, 'wb') as file:
            file.write(response.content)

        print(f"Downloaded {pdf_url} to {file_name}")

    driver.quit()

def main():
    base_url = 'https://www.vldb.org/pvldb/volumes/'
    for volume in range(14, 0, -1):
        url = base_url + str(volume)
        download_pdf(url)

# Call the main function
main()