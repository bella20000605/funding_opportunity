from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


# Set the download directory (your local path)
download_dir = os.path.join(os.getcwd(), 'downloads')  # This will save it in a "downloads" folder within your project

# Create the directory if it doesn't exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

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

# Step 5: Find the keyword input field and enter the search term
search_box = driver.find_element(By.ID, 'inp-keywords')
search_box.send_keys('Global Health Security')  # Replace with search keyword
search_box.send_keys(Keys.RETURN)

# Step 6: Wait for the search results to load using explicit waits (ensuring that the page has fully loaded before interacting with elements)
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Export Results')))
except Exception as e:
    print(f"Error while waiting for the search results to load: {e}")
    driver.quit()

# Step 7: Find and click the 'Export Results' link to download the CSV
try:
    export_button = driver.find_element(By.LINK_TEXT, 'Export Results')  # Ensure this link text is correct
    export_button.click()
except Exception as e:
    print(f"Error while trying to find or click the export button: {e}")

# Step 8: Wait for the file to download (adjust time as needed)
time.sleep(10)  # Adjust the sleep time based on the actual time it takes for the download

# Step 9: Close the browser after the download is complete
driver.quit()

print(f"CSV file downloaded successfully to {download_dir}!")
