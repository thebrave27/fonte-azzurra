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
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36"
}

# === FUNZIONE DI FALLBACK ===
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
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = title_tag["href"]
            date_tag = post.select_one("time")
            published = date_tag.text.strip() if date_tag else str(datetime.now())
            results.append({
                "title_it": title,
                "title_en": title,
                "link": link,
                "published": published,
                "source": "comunicati"
            })
        print(f"   ✅ {len(results)} comunicati estratti da HTML")
    except Exception as e:
        print(f"   ⚠️ Fallback SSC Napoli fallito: {e}")
    return results

# === RACCOLTA ARTICOLI ===
articles = []

for key, urls in feeds.items():
    print(f"📰 Scarico feed: {key}")
    success = False
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            if feed.entries:
                for entry in feed.entries:
                    articles.append({
                        "title_it": entry.title,
                        "title_en": entry.title,
                        "link": entry.link,
                        "published": entry.published if 'published' in entry else str(datetime.now()),
                        "source": key
                    })
                print(f"   ✅ {len(feed.entries)} articoli trovati da {url}")
                success = True
                break
            else:
                print(f"   ⚠️ Nessun contenuto nel feed: {url}")
        except Exception as e:
            print(f"   ⚠️ Errore per {url}: {e}")
    if not success:
        print(f"   ❌ Nessun feed valido trovato per {key}")
        if key == "comunicati":
            fallback = fallback_sscnapoli()
            articles.extend(fallback)

# === SALVATAGGIO DATI ===
if not articles:
    print("⚪ Nessun nuovo articolo trovato")
else:
    print(f"🟢 Totale articoli raccolti: {len(articles)}")

feed_path = "feed.json"
history_path = "storico.json"

# Carica storico precedente
if os.path.exists(history_path):
    with open(history_path, "r", encoding="utf-8") as f:
        storico = json.load(f)
else:
    storico = []

# Unisci senza duplicati (basato sul link)
links_esistenti = {item["link"] for item in storico}
nuovi = [a for a in articles if a["link"] not in links_esistenti]
storico = nuovi + storico  # aggiungi nuovi in cima

# Salva file aggiornati
with open(feed_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f"💾 Salvato feed.json con {len(articles)} articoli")

with open(history_path, "w", encoding="utf-8") as f:
    json.dump(storico, f, ensure_ascii=False, indent=2)
print(f"💾
