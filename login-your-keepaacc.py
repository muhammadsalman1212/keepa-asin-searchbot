import glob
import json
import os
import random
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime



with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        headless=False, user_data_dir=r'C:\Users\ULC\PycharmProjects\final-keepa-asinsearch-bot\user_data_dir')
    page = browser.new_page()
    page.goto("https://keepa.com/", timeout=0)
    page.wait_for_timeout(1000000)


