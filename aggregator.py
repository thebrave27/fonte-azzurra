import sys
import subprocess

# Installa i moduli necessari se non presenti
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import feedparser
except ModuleNotFoundError:
    install("feedparser")
    import feedparser

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    install("beautifulsoup4")
    from bs4 import BeautifulSoup

import json
import requests
from datetime import datetime
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
            try:
                title_tag = post.select_one("h2 a")
                link_tag = post.select_one("h2 a")
                date_tag = post.select_one("time")
                
                title = title_tag.get_text(strip=True) if title_tag else "Senza titolo"
                link = link_tag['href'] if link_tag and link_tag.has_attr('href') else "#"
                date = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else None
                
                results.append({
                    "title": title,
                    "link": link,
                    "date": date
                })
            except Exception as e:
                print(f"⚠️ Errore parsing articolo: {e}")
    except Exception as e:
        print(f"❌ Errore nel fallback SSC Napoli: {e}")
    return results

# === ESEMPIO USO ===
if __name__ == "__main__":
    comunicati = fallback_sscnapoli()
    print(f"✅ Estratti {len(comunicati)} comunicati:")
    for c in comunicati:
        print(f"- {c['title']} ({c['link']})")
