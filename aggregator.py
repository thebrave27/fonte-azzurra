import feedparser
import json
import requests
from datetime import datetime

print("🔵 Avvio aggiornamento Fonte Azzurra...")

# Feed ufficiali SSC Napoli
feeds = {
    "comunicati": "https://www.sscnapoli.it/category/comunicati-stampa/feed/",
    "youtube": "https://www.youtube.com/feeds/videos.xml?channel_id=UCsYjM4I1zogVxZtkvOSN49A",
    "radio": "https://www.radiokisskiss.it/feed/"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}

articles = []

for key, url in feeds.items():
    print(f"📰 Scarico feed: {key} → {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        print(f"   ➜ {len(feed.entries)} articoli trovati")
        for entry in feed.entries:
            articles.append({
                "title_it": entry.title,
                "title_en": entry.title,
                "link": entry.link,
                "published": entry.get("published", str(datetime.now())),
                "source": key
            })
    except Exception as e:
        print(f"   ⚠️ Errore nel download del feed {key}: {e}")

if not articles:
    print("⚪ Nessun nuovo articolo trovato")
else:
    print(f"🆕 Trovati {len(articles)} articoli totali")

# Salva feed JSON
feed_path = "feed.json"
with open(feed_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f"💾 Salvato {feed_path} con {len(articles)} articoli")

# Genera HTML
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
