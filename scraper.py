"""
Twitter/X Market Intelligence Scraper (Latest ~100 Tweets + Google Sheets)
Scrapes around 100 live tweets (≈25 per hashtag) and overwrites
a Google Sheet with the latest results on every run.
"""

import time
import re
import logging
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import getpass

# -------------------------------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------------------------------
logging.basicConfig(
    filename="twitter_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------------------------------------------------
# DRIVER INITIALIZATION
# -------------------------------------------------------------------------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# -------------------------------------------------------------------------
# LOGIN HANDLER — FULLY DYNAMIC
# -------------------------------------------------------------------------
def login_to_twitter(driver, username, password):
    driver.get("https://twitter.com/login")
    print("🔑 Logging into Twitter...")
    wait = WebDriverWait(driver, 25)

    # Step 1: Username
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_field.send_keys(username)
    username_field.send_keys(Keys.RETURN)
    time.sleep(3)

    # Step 2: Optional confirmation
    try:
        next_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        if next_field:
            print("🌀 Twitter requested confirmation (email/username)...")
            next_field.send_keys(username)
            next_field.send_keys(Keys.RETURN)
            time.sleep(3)
    except Exception:
        pass

    # Step 3: Password
    try:
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(6)
        print("✅ Logged in successfully.")
    except Exception:
        print("⚠️ Password field not found — please log in manually in the browser window.")
        input("After manual login, press ENTER to continue...")

# -------------------------------------------------------------------------
# SCRAPE FUNCTION — LATEST TWEETS
# -------------------------------------------------------------------------
def scrape_tweets(driver, hashtags, total_limit=100):
    all_tweets = []
    per_tag_limit = total_limit // len(hashtags)

    for tag in hashtags:
        url = f"https://twitter.com/search?q=%23{tag}&src=typed_query&f=live"
        driver.get(url)
        time.sleep(5)
        print(f"🔍 Scraping latest #{tag} tweets...")

        last_height = driver.execute_script("return document.body.scrollHeight")
        tag_tweets = 0

        while len(all_tweets) < total_limit and tag_tweets < per_tag_limit:
            tweets = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            for t in tweets:
                try:
                    spans = t.find_elements(By.XPATH, ".//div[@data-testid='tweetText']//span")
                    content = " ".join([span.text for span in spans]).strip()
                    if not content:
                        continue
                    if any(content == tw.get("content") for tw in all_tweets):
                        continue

                    username_elems = t.find_elements(By.XPATH, ".//span[contains(text(), '@')]")
                    username = username_elems[0].text if username_elems else "unknown"

                    timestamp = datetime.now().isoformat()
                    mentions = re.findall(r"@\w+", content)
                    hashtags_found = re.findall(r"#\w+", content)

                    tweet = {
                        "hashtag": f"#{tag}",
                        "username": username,
                        "timestamp": timestamp,
                        "content": content,
                        "mentions": ", ".join(mentions),
                        "hashtags": ", ".join(hashtags_found)
                    }

                    all_tweets.append(tweet)
                    tag_tweets += 1

                    if len(all_tweets) >= total_limit or tag_tweets >= per_tag_limit:
                        break
                except Exception as e:
                    logging.warning(f"Tweet parse error: {e}")
                    continue

            if len(all_tweets) >= total_limit or tag_tweets >= per_tag_limit:
                break

            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print(f"✅ Collected {tag_tweets} tweets for #{tag}")

    df = pd.DataFrame(all_tweets)
    df.drop_duplicates(subset=["content"], inplace=True)
    print(f"✅ Final total tweet count: {len(df)}")
    return df.head(total_limit)

# -------------------------------------------------------------------------
# GOOGLE SHEETS UPLOADER (OVERWRITE)
# -------------------------------------------------------------------------
def write_df_to_gsheet_overwrite(df: pd.DataFrame):
    df_to_write = df.copy()
    for col in df_to_write.columns:
        df_to_write[col] = df_to_write[col].astype(str)

    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    sheet_url = os.environ.get("TARGET_SHEET_URL")
    service_account_path = os.environ.get("SERVICE_ACCOUNT_JSON")

    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPE)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(sheet_url)
    ws = sh.get_worksheet(0)
    ws.clear()

    set_with_dataframe(ws, df_to_write, include_index=False, include_column_header=True, resize=True)
    print(f"✅ Overwrote Google Sheet: {sh.title} ({len(df)} rows)")

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
if __name__ == "__main__":
    hashtags = ["nifty50", "sensex", "intraday", "banknifty"]

    print("🔒 Enter your Twitter credentials (won’t be stored):")
    username = input("Username or email: ")
    password = getpass.getpass("Password: ")

    driver = init_driver()
    login_to_twitter(driver, username, password)

    print("🚀 Starting live scraping (~100 tweets total)...")
    df_raw = scrape_tweets(driver, hashtags, total_limit=100)
    driver.quit()

    if not df_raw.empty:
        write_df_to_gsheet_overwrite(df_raw)
    else:
        print("⚠️ No tweets collected. Nothing to upload.")
