import feedparser
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("🔵 Avvio aggiornamento Fonte Azzurra...")

# === CONFIG ===
feeds = {
    "comunicati": [
        "https://www.sscnapoli.it/category/comunicati-stampa/feed/",
        "https://www.sscnapoli.it/feed/",
        "https://www.sscnapoli.it/feed/?cat=15"
    ],
    "youtube": [
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCTnCzHi0P6MH83er5OfZbzQ"
    ],
    "radio": [
        "https://www.radiokisskiss.it/feed/"
    ]
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0 Safari/537.36"
}

# === FALLBACK ===
def fallback_sscnapoli():
    """Estrae comunicati direttamente dal sito SSC Napoli se il feed RSS non risponde."""
    print("🧩 Fallback attivo: estraggo comunicati dal sito SSC Napoli...")
    url = "https://sscnapoli.it/category/comunicati-stampa/"
    results = []
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        posts = soup.select("article")
        for post in posts[:10]:
            title_tag = post.select_one("h2 a")
