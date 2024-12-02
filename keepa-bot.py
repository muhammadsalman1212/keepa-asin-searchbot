import glob
import json
import os
import random
import time
import shutil
from pathlib import Path
import csv
import pandas as pd
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime
# pip install playwright
# playwright install
# pip install pandas, requests
import time
from datetime import datetime
import requests



def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()





# Send the message

# Load the CSV file into a DataFrame
df = pd.read_csv(r'C:\Users\ULC\PycharmProjects\final-keepa-asinsearch-bot\right-format-ofasins.csv', dtype={'Asin': str})

# Extract the columns into separate lists
asin_list = df['Asin'].tolist()
set_price_list = df['Set_Price'].tolist()

# Output the lists
print("Asin:", asin_list)
print("Set_Price:", set_price_list)

with sync_playwright() as p:
    # Initialize start time for hourly restart
    start_time = time.time()

    browser = p.chromium.launch_persistent_context(
        headless=False,
        user_data_dir='user_data_dir',
        args=[
            "--disable-dev-shm-usage",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
        ]
    )
    page = browser.new_page()
    page.goto("https://keepa.com/", timeout=0)

    for all_asins, all_prices in zip(asin_list, set_price_list):
        # Check if 1 hour has passed
        if time.time() - start_time >= 3600:  # 1 hour = 3600 seconds
            print("Restarting the browser after 2 minuites.")
            browser.close()  # Close the current browser context
            browser = p.chromium.launch_persistent_context(
                headless=False,
                user_data_dir=r'C:\Users\ULC\PycharmProjects\final-keepa-asinsearch-bot\user_data_dir',
                args=[
                    "--disable-dev-shm-usage",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                ]
            )
            page = browser.new_page()  # Open a new page in the restarted browser
            start_time = time.time()  # Reset the timer

        page.goto("https://keepa.com/", timeout=0)
        print(f"{all_asins} this asin")
        now = datetime.now()
        current_time = now.strftime("%H:%M")  # Renamed 'time' to 'current_time'
        day = now.day
        year = now.year

        date_format = f'{current_time}/{day}/{year}'
        time.sleep(1)

        process_successor_wrong = None  # Initialize variable to track the ASIN's status
        page.click("//span[text()='Suche']", timeout=0)  # Click on search button
        # Search for the ASIN
        time.sleep(1)
        page.fill('//input[@id="searchInput"]', str(all_asins), timeout=0)  # Search the ASIN
        print(f"{asin_list} asin searched")
        page.keyboard.press("Enter")  # Press enter key
        print('asin entered')
        time.sleep(3)
        try:
            page.click('(//ul[@id="tabHead"])//li[2]', timeout=1000)  # Click on Preis überwachen button
            print(" Clicked on Preis überwachen button")
        except Exception:
            success_fully_process = "Not Success Processed"
            print(f"ASIN {all_asins} is not found on Keepa. Skipping to the next ASIN. Status: {success_fully_process}")
            continue

        # Check if the specified text is present within 20 seconds
        try:
            element = page.locator("//p[text()='Dieses Produkt wird bereits für dich überwacht.']")
            print('Clicked on overwrite button')
            element.wait_for(timeout=500)  # Wait for up to 20 seconds
            # If the element is found, set the variable and skip to the next ASIN
            process_successor_wrong = "ASIN already used"  # Mark the ASIN as already used
            overwrite_button = page.click(
                '//button[@id="updateTracking" and contains(., "Aktualisiere bestehende Überwachung")]', timeout=0)
            over_write = True

        except Exception:
            over_write = False
            print("ASIN is new")
            pass
        time.sleep(2)
        # Proceed with further actions if the ASIN was not already used
        # remove_but_price_value
        # page.fill('//input[@name="csvtype-3-18-threshold"]', "")
        page.fill('//div[label[contains(., "Amazon")]]//input[@type="text"]', str(all_prices),
                  timeout=0)  # Fill the price input
        print(f"price filled with this {all_prices}")
        time.sleep(1)
        # Click on the country icon
        page.click('//div[@class="tracking__tab-bar-toggle"]//i', timeout=0)
        print(f"clicked on country icon")
        # Click on the Europia button
        page.click('//span[@class="tracking__multilocale-select-all" and contains(., "Europa")]', timeout=0)
        print('clicked on europa all button')
        time.sleep(1)
        # Uncheck the UK country
        page.click('//input[@value="2"]', timeout=0)
        print('clicked on uk Uncheck button')
        time.sleep(1.5)
        # Click on Aktiviere ausgewählte Domains button
        page.click('//button[@id="multilocale__submit" and contains(., "Aktiviere ausgewählte Domains")]', timeout=0)
        print('clicked on Aktiviere ausgewählte Domains button')
        page.click('//li[text()="Preis überwachen"]', timeout=0)
        print("again clicked on ")

        time.sleep(2)
        # Select 10 years option
        page.select_option('#tracking-ttl', value="87600")  # Click on 10 jahre option button

        time.sleep(2)
        # Click on Wunschpreis button
        if over_write == True:
            page.click('//button[@id="submitTracking" and contains(., "Preisüberwachung aktualisieren")]', timeout=0)
            print('clicked on Preisüberwachung aktualisieren')
        else:
            page.click('//button[@id="submitTracking" and contains(., "Wunschpreis Überwachung abschicken")]',
                       timeout=0)
            print('clicked on Wunschpreis Überwachung abschicken button')

        # //div[text()="Tracking Limit Reached"]
        try:
            text = page.locator('//div[text()="Tracking Limit Reached"]').inner_text(timeout=2000)
            # response = send_telegram_message(bot_token, chat_id, message)
            # print(response)
            print('Tracking Limit Reached')
            break
        except:
            pass

        time.sleep(2)
        success_fully_process = "Successfully Processed"

        print(f'Finished processing ASIN {all_asins} with status: {success_fully_process}')

        header = ["Asin", "Set_Price", "Status", 'Date']
        with open(f'done-asins.csv', 'a+', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Check if file is empty
                writer.writerow(header)
            writer.writerow(
                [all_asins, all_prices, success_fully_process, date_format])
        page.reload(timeout=0)
    # send_telegram_message(bot_token, chat_id, 'Process Done')
