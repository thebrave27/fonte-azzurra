import feedparser
import json
import requests
from datetime import datetime

print("🔵 Avvio aggiornamento Fonte Azzurra...")

feeds = {
    "comunicati": [
        "https://www.sscnapoli.it/category/comunicati-stampa/feed/",
        "https://www.sscnapoli.it/feed/",
        "https://www.sscnapoli.it/feed/?cat=15"
    ],
    "youtube": ["https://www.youtube.com/feeds/videos.xml?channel_id=UC6Z8Q2b_jt2Tf-G4U0v88MQ"],
    "radio": ["https://www.radiokisskiss.it/feed/"]
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}

articles = []

for key, urls in feeds.items():
    success = False
    for url in urls:
        print(f"📰 Scarico feed: {key} → {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            if feed.entries:
                print(f"   ✅ {len(feed.entries)} articoli trovati")
                for entry in feed.entries:
                    articles.append({
                        "title_it": entry.title,
                        "title_en": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", str(datetime.now())),
                        "source": key
                    })
                success = True
                break
        except Exception as e:
            print(f"   ⚠️ Errore per {url}: {e}")
    if not success:
        print(f"   ❌ Nessun feed valido trovato per {key}")

if not articles:
    print("⚪ Nessun nuovo articolo trovato")
else:
    print(f"🆕 Trovati {len(articles)} articoli totali")

with open("feed.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

html_content = ""
for art in articles:
    html_content += f"""
    <article>
      <div class='title'>{art['title_it']}</div>
      <div class='date'>{art['published']}</div>
      <a href='{art['link']}' target='_blank'>Leggi / Watch</a>
    </article>
    """

try:
    with open("index.html", "r", encoding="utf-8") as f:
        template = f.read()
    template = template.replace("<!-- Gli articoli saranno generati automaticamente dallo script Python -->", html_content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)
    print("✅ index.html aggiornato con gli articoli")
except FileNotFoundError:
    print("⚠️ index.html non trovato – salto aggiornamento HTML")

print("✅ Aggiornamento completato con successo!")
