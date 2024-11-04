import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Set the download directory (your local path)
download_dir = os.path.join(os.getcwd(), 'downloads')  # This will save it in a "downloads" folder within your project

# Create the directory if it doesn't exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set up the directory for final output
final_output_dir = os.path.join(os.getcwd(), 'downloads_website')
if not os.path.exists(final_output_dir):
    os.makedirs(final_output_dir)

# Step 1: Set Chrome options to configure the download location
chrome_options = webdriver.ChromeOptions()

prefs = {
    "download.default_directory": download_dir,  # Set the directory where the file will be saved
    "download.prompt_for_download": False,  # Avoid the popup asking where to save the file
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True  # Ensure safe browsing is enabled
}

chrome_options.add_experimental_option("prefs", prefs)

# Enable headless mode when running in a server environment (GitHub Actions)
chrome_options.add_argument('--headless')  # Comment out if you want to see the browser UI locally
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Step 2: Use ChromeDriverManager to manage the driver version
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Step 3: Open Grants.gov search page
driver.get('https://www.grants.gov/search-grants.html')

# Step 4: Wait for the page to load
time.sleep(3)

# Step 5: Prepare search terms in sections
search_terms = [
    ["Global Health Security and Epidemiology", '"global health security", "Epidemiology"'],
    ["HIV/AIDS", '"HIV", "AID", "HIV prevention" OR "HIV treatment" OR "HIV services" OR "HIV sustainability"'],
    ["Infectious Diseases", '"Infectious Disease", "Tuberculosis"'],
    ["Non-communicable Diseases", '"Non-communicable Disease"'],
    ["Public Health and Related Terms", '"Public Health", "Vaccines", "Antimicrobial Resistance", "Social Determinants"'],
    ["Adolescent Health", '"Adolescent Girls Young Women" OR "AGYW", "Adolescent Boys Young Men" OR  "ABYM"'],
    ["Health Systems Strengthening", '"Health Systems Strengthening", "Integrated Health Systems"'],
    ["Human Resources for Health", '"Human Resources for Health", "Health Worker Retention", "Health Worker Migration"'],
    ["Health Financing", '"Health Financing"'],
    ["Health Systems Policy and Research", '"Health Systems Policy", "Health Systems Research"']
]

# Step 6: Initialize the final DataFrame for all results
final_results = pd.DataFrame()

# Helper function to detect the most recent file in the download folder
def get_latest_file(directory):
    files = os.listdir(directory)
    paths = [os.path.join(directory, basename) for basename in files if basename.endswith('.csv')]
    return max(paths, key=os.path.getctime) if paths else None

# Helper function to sanitize file names (replace special characters like slashes)
def sanitize_filename(name):
    return name.replace("/", "_").replace("\\", "_").replace(" ", "_")

# Step 7: Perform search queries from search terms list
for category, terms in search_terms:
    term_list = terms.split(", ")  # Split terms by comma for individual searches
    print(f"Searching for terms in category: {category}")
    
    for term in term_list:
        print(f"Searching for: {term}")
        # Step 8: Find the keyword input field and enter the search term
        search_box = driver.find_element(By.ID, 'inp-keywords')
        search_box.clear()  # Clear previous search
        search_box.send_keys(term.strip())  # Ensure each term is trimmed and searched individually
        
        # Step 9: Click the 'Search' button using the button's ID
        search_button = driver.find_element(By.ID, 'btn-search')
        search_button.click()  # Simulate a click on the search button

        time.sleep(3)  # Wait for the search results to load

        # Step 10: Wait for the search results to load using explicit waits
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Export Results')))
        except Exception as e:
            print(f"Error while waiting for the search results to load for term {term}: {e}")
            continue  # Skip to the next term

        # Step 11: Find and click the 'Export Results' link to download the CSV
        try:
            export_button = driver.find_element(By.LINK_TEXT, 'Export Results')  # Ensure this link text is correct
            export_button.click()
        except Exception as e:
            print(f"Error while trying to find or click the export button for term {term}: {e}")

        # Step 12: Wait for the file to download (adjust time as needed)
        time.sleep(5)  # Increased wait time for larger downloads or network delays

        # Step 13: Detect the latest downloaded CSV file and rename it
        latest_file = get_latest_file(download_dir)
        if latest_file:
            new_file_name = os.path.join(download_dir, f"{sanitize_filename(term)}_results.csv")
            os.rename(latest_file, new_file_name)
            print(f"Renamed downloaded file to: {new_file_name}")

            # Step 14: Read the downloaded file and append to final_results
            try:
                df = pd.read_csv(new_file_name)
                df["Search Term"] = term  # Add a column for the search term
                final_results = pd.concat([final_results, df], ignore_index=True)
            except Exception as e:
                print(f"Error reading the file {new_file_name}: {e}")
        else:
            print(f"No file detected for term {term}")


# Step 15: Save final_results to a combined CSV file in downloads_website folder
final_output_path = os.path.join(final_output_dir, 'Final_grants.gov.csv')
final_results.to_csv(final_output_path, index=False)
print(f"Combined CSV file created successfully at {final_output_path}")


# Step 16: Close the browser after the download is complete
driver.quit()

print(f"Search and download process completed successfully!")
