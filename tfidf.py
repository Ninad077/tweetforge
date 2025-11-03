import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt
import seaborn as sns

# --- Read Google Sheet ---
def read_sheet():
    sheet_url = os.environ.get("TARGET_SHEET_URL")
    service_account_path = os.environ.get("SERVICE_ACCOUNT_JSON")

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    gc = gspread.authorize(Credentials.from_service_account_file(service_account_path, scopes=scope))
    ws = gc.open_by_url(sheet_url).sheet1
    return pd.DataFrame(ws.get_all_records())

# --- Convert text to signals ---
def text_to_signal(df):
    vec = TfidfVectorizer(max_features=500, stop_words='english')
    X = vec.fit_transform(df['content'])
    pca = PCA(n_components=1)
    df['signal'] = pca.fit_transform(X.toarray())
    df['signal'] = (df['signal'] - df['signal'].mean()) / df['signal'].std()
    return df

# --- Analytical & Beautiful Plot with Custom Colors ---
def plot_signal(df):
    sns.set(style='whitegrid', context='talk', font_scale=0.9)
    plt.figure(figsize=(11, 6))
    sample = df.sample(min(600, len(df))).sort_index()

    # Custom dark color mapping
    palette = {
        '#banknifty': '#8B0000',   # dark red
        '#nifty50': '#4B0082',     # dark violet
        '#sensex': '#006400',      # dark green
        '#intraday': '#FF8C00'     # dark orange
    }

    sns.scatterplot(
        x=sample.index,
        y=sample['signal'],
        hue=sample['hashtag'],
        palette=palette,
        s=70,
        alpha=0.9,
        edgecolor='white'
    )

    # Moving average trend (dark brown)
    rolling_mean = sample['signal'].rolling(window=5, min_periods=1).mean()
    plt.plot(sample.index, rolling_mean, color='#5C4033', linewidth=2.2, alpha=0.9, label='5-point Avg Trend')

    # Mean line and annotation
    mean_signal = sample['signal'].mean()
    plt.axhline(mean_signal, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    plt.text(sample.index.max() * 0.9, mean_signal + 0.05, f'Mean: {mean_signal:.2f}', color='gray')

    # Styling
    plt.title('📊 Tweet Sentiment Signal Analysis', fontsize=18, weight='bold', pad=15)
    plt.xlabel('Tweet Index (Chronological Order)', fontsize=12)
    plt.ylabel('Normalized Signal Strength (Z-score)', fontsize=12)
    plt.legend(title='Hashtag', loc='best', frameon=True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df = read_sheet()
    df = text_to_signal(df)
    plot_signal(df)
    print(df[['username', 'hashtag', 'signal']].head())
