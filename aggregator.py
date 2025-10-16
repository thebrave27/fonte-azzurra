import feedparser
import json
from datetime import datetime
import os

print("🔵 Avvio aggiornamento Fonte Azzurra...")

# Percorso assoluto (per evitare errori su GitHub Actions)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Feed ufficiali SSC Napoli
feeds = {
    "comunicati": "https://www.sscnapoli.it/category/comunicati-stampa/feed/",
    "youtube": "https://www.youtube.com/feeds/videos.xml?channel_id=UCsYjM4I1zogVxZtkvOSN49A",
    "radio": "https://www.radiokisskiss.it/feed/"
}

articles = []

for key, url in feeds.items():
    print(f"📰 Scarico feed: {key} → {url}")
    feed = feedparser.parse(url)
    print(f"   ➜ {len(feed.entries)} articoli trovati")

    for entry in feed.entries:
        published = entry.get("published", str(datetime.now()))
        articles.append({
            "title_it": entry.title,
            "title_en": entry.title,
            "link": entry.link,
            "published": published,
            "source": key
        })

# Percorsi file
feed_path = os.path.join(BASE_DIR, "feed.json")
storico_path = os.path.join(BASE_DIR, "storico.json")
index_path = os.path.join(BASE_DIR, "index.html")

# Carica storico precedente
try:
    with open(storico_path, "r", encoding="utf-8") as f:
        storico = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    storico = []

# Aggiungi solo nuovi articoli
nuovi = [a for a in articles if a["link"] not in [s["link"] for s in storico]]
if nuovi:
    print(f"🆕 {len(nuovi)} nuovi articoli trovati")
    storico.extend(nuovi)
else:
    print("⚪ Nessun nuovo articolo trovato")

# Salva i file aggiornati
with open(feed_path, "w", encoding="utf-8") as f_
