
# 🐦 **tweetforge**  
### *Web-scraping, vectorizing & visualizing market sentiment from Twitter/X*

> A repository to webscrape X's (Twitter’s) tweets, perform text vectorization, and generate visual market insights.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Selenium-Automation-green?logo=selenium&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Sheets-API-yellow?logo=google-sheets&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-orange" />
</p>

---

## 📖 **Overview**

**tweetforge** automates **Twitter/X market sentiment scraping and signal analysis** using Python, Selenium, and Google Sheets.

It scrapes **~100 of the latest live tweets** for specific finance hashtags, stores them in a Google Sheet, and then performs **TF-IDF + PCA signal analysis** to visualize real-time sentiment trends in financial markets.

---

## 🧩 **Project Architecture**

tweetforge/
│
├── scraper.py # Scrapes live tweets & uploads to Google Sheet
├── tfidf.py # Reads the Sheet & performs sentiment/signal analysis
├── twitter_scraper.log # Log file generated after running scraper.py
│
├── requirements.txt # Python dependencies
├── .gitignore # Prevents credentials/logs from being tracked
└── .env # (optional) Local secret configuration


---

## 🚀 **Features**

### 🧾 **`scraper.py`**
- 🔍 Scrapes live tweets (≈25 per hashtag)
- 🔐 Logs in dynamically (manual fallback supported)
- 🧠 Extracts username, content, hashtags, mentions, timestamp
- ☁️ Uploads results directly to **Google Sheets** (auto-overwrites)
- 🧩 Secure — reads secrets from environment variables

---

### 📊 **`tfidf.py`**
- 📥 Reads the Google Sheet created by `scraper.py`
- 🧮 Converts text → TF-IDF vectors → PCA signal
- 🔄 Normalizes the signal to a Z-score
- 🎨 Generates a **color-coded scatterplot** with trend lines
- 📈 Visualizes live sentiment shifts for each hashtag

---

## 🔐 **Secure Configuration**

This project is designed to **protect credentials** for both local and GitHub environments.

### 🧩 1️⃣ Local Setup – `.env` File
Create a `.env` file in your root directory:
```bash
TARGET_SHEET_URL="https://docs.google.com/spreadsheets/d/your_sheet_id/edit#gid=0 : Your target GSheet :)"
SERVICE_ACCOUNT_JSON=" You got to have this file :)"





tweetforge/
│
├── scraper.py # Scrapes live tweets & uploads to Google Sheet
├── tfidf.py # Reads the Sheet & performs sentiment/signal analysis
├── twitter_scraper.log # Log file generated after running scraper.py
│
├── requirements.txt # Python dependencies
├── .gitignore # Prevents credentials/logs from being tracked
└── .env # (optional) Local secret configuration


---

| Requirement                      | Description                                  |
| -------------------------------- | -------------------------------------------- |
| **Python ≥ 3.9**                 | Required for latest library compatibility    |
| **Google Cloud Service Account** | Must have Sheets + Drive API access          |
| **Google Sheet URL**             | Target sheet to write scraped data           |
| **Chrome Browser**               | Required for Selenium automation             |
| **ChromeDriver**                 | Managed automatically by `webdriver-manager` |





-----
⚙️ Installation

Clone this repository and install dependencies:

git clone https://github.com/Ninad077/tweetforge.git
cd tweetforge
pip install -r requirements.txt


🧾 Usage
🥇 Step 1 — Run the Scraper
python scraper.py


Prompts for Twitter login credentials (not stored)

Scrapes tweets for default hashtags:

nifty50, sensex, intraday, banknifty


Uploads the latest 100 tweets to your Google Sheet

Output:

twitter_scraper.log — scraper activity log

Updated Google Sheet — new tweet dataset

🥈 Step 2 — Run the Analyzer
python tfidf.py


Fetches tweets from the same Google Sheet

Transforms text into TF-IDF vectors

Performs PCA dimensionality reduction

Normalizes signal values

Generates a visual sentiment trend chart

🧮 Example Google Sheet Schema
hashtag	username	timestamp	content	mentions	hashtags
#nifty50	@abcuser	2025-11-03T10:23:12Z	Market looks strong today	@nseindia	#nifty50, #sensex
📈 Example Visualization

The output chart displays:

Scatter points = tweet-level signals

Distinct colors per hashtag:

🟥 #banknifty

🟪 #nifty50

🟩 #sensex

🟧 #intraday

Smooth brown line for 5-point moving average

💡 Visualizes real-time market mood fluctuations based on financial tweet sentiment.
