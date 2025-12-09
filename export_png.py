import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CERT_DIR = 'certificate'
PNG_DIR = 'certificate/png'

# Ensure output directory exists
os.makedirs(PNG_DIR, exist_ok=True)

# List all HTML files in certificate folder
html_files = [f for f in os.listdir(CERT_DIR) if f.endswith('.html')]

# Set up Chrome in headless mode
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--window-size=1300,900')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--force-device-scale-factor=2')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Path to chromedriver (update if needed)
driver = webdriver.Chrome(options=chrome_options)

for html_file in html_files:
    roll = os.path.splitext(html_file)[0]
    file_path = os.path.abspath(os.path.join(CERT_DIR, html_file))
    file_url = f'file:///{file_path.replace(os.sep, "/")}'
    print(f'Processing {html_file} ...')
    driver.get(file_url)
    time.sleep(2)  # Wait for page and fonts to load

    # Run the downloadPNG function in the page
    driver.execute_script('downloadPNG();')
    time.sleep(2)  # Wait for canvas and download

    # Find the canvas and save as PNG
    try:
        canvas = driver.find_element(By.TAG_NAME, 'canvas')
        png_data = canvas.screenshot_as_png
        out_path = os.path.join(PNG_DIR, f'{roll}.png')
        with open(out_path, 'wb') as f:
            f.write(png_data)
        print(f'Saved {out_path}')
    except Exception as e:
        print(f'Failed for {html_file}: {e}')

# Clean up
driver.quit()
print('All done!')
