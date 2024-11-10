# scraper.py

import os  
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def scrape_data(output_file='products.csv'):
    service = Service('C:\\Users\\itm\\Downloads\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    watches_list = []
    page_number = 1

    if not os.path.exists(output_file):
        pd.DataFrame(columns=['Title', 'Location', 'Price', 'Discount', 'Sec_Info', 'Shipping', 'Sold']).to_csv(output_file, index=False)

    while True:
        url = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw=watch&_sacat=0&rt=nc&_ipg=240&_pgn={page_number}"
        driver.get(url)

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 's-item'))
            )
            time.sleep(5)  
        except TimeoutException:
            print(f"Timeout while loading page {page_number}.")
            break  

        watches = driver.find_elements(By.CLASS_NAME, 's-item')

        for j in range(len(watches)):
            try:
                watch = watches[j]
                
                location = watch.find_element(By.CLASS_NAME, 's-item__location').text.strip() if watch.find_elements(By.CLASS_NAME, 's-item__location') else 'N/A'
                sec_info = watch.find_element(By.CLASS_NAME, 'SECONDARY_INFO').text.strip() if watch.find_elements(By.CLASS_NAME, 'SECONDARY_INFO') else 'N/A'
                price = watch.find_element(By.CLASS_NAME, 's-item__price').text.strip() if watch.find_elements(By.CLASS_NAME, 's-item__price') else 'N/A'
                title = watch.find_element(By.CSS_SELECTOR, '.s-item__title span[role="heading"]').text.strip() if watch.find_elements(By.CSS_SELECTOR, '.s-item__title span[role="heading"]') else 'N/A'
                discount = 'N/A'
                sold = 'N/A'
                
                bold_elements = watch.find_elements(By.CLASS_NAME, 'BOLD')
                if bold_elements:
                    if len(bold_elements) > 0:
                        discount_text = bold_elements[0].text.strip()
                        if 'off' in discount_text.lower():
                            discount = discount_text
                    if len(bold_elements) > 1:
                        sold_text = bold_elements[1].text.strip()  
                        if 'sold' in sold_text.lower():
                            sold = sold_text

                shipping = watch.find_element(By.CLASS_NAME, 's-item__shipping').text.strip() if watch.find_elements(By.CLASS_NAME, 's-item__shipping') else 'N/A'
                watches_list.append({
                    'Title': title,
                    'Location': location, 
                    'Price': price, 
                    'Discount': discount, 
                    'Sec_Info': sec_info,
                    'Shipping': shipping,
                    'Sold': sold
                })

            except NoSuchElementException as e:
                print(f"Error processing watch {j} on page {page_number}: No such element - {e}")
            except Exception as e:
                print(f"Error processing watch {j} on page {page_number}: {e}")

        df = pd.DataFrame(watches_list)
        df.to_csv(output_file, mode='a', header=False, index=False)
        watches_list.clear()  
        
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'pagination__next')
            if "pagination__next--disabled" in next_button.get_attribute("class"):
                print("Last page reached")
                break
            else:
                page_number += 1
                time.sleep(2)  
        except NoSuchElementException:
            print(f"Next button not found on page {page_number}.")
            break
        except Exception as e:
            print(f"Error while checking next button on page {page_number}: {e}")
            break

    driver.quit()
