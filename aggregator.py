import feedparser
import json
from datetime import datetime
import os

# Feed ufficiali SSC Napoli
feeds = {
    "comunicati": "https://www.sscnapoli.it/category/comunicati-stampa/feed/",
    "youtube": "https://www.youtube.com/feeds/videos.xml?channel_id=UCsYjM4I1zogVxZtkvOSN49A",
    "radio": "https://www.radiokisskiss.it/feed/"
}

articles = []

# Carica archivio esistente (se già presente)
if os.path.exists("storico.json"):
    with open("storico.json", "r", encoding="utf-8") as f:
        try:
            articles = json.load(f)
        except json.JSONDecodeError:
            articles = []

# Raccogli nuovi articoli dai feed
for key, url in feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        new_item = {
            "title_it": entry.title,
            "title_en": entry.title,  # traduzione manuale opzionale
            "link": entry.link,
            "published": entry.published if 'published' in entry else str(datetime.now()),
            "source": key
        }

        # Aggiungi solo se non è già presente
        if not any(a["link"] == new_item["link"] for a in articles):
            articles.append(new_item)

# Ordina articoli per data (più recente in alto)
articles = sorted(articles, key=lambda x: x["published"], reverse=True)

# Salva archivio completo
with open("storico.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

# Salva anche una versione ridotta (solo ultimi 20) per uso web
recent_articles = articles[:20]
with open("feed.json", "w", encoding="utf-8") as f:
    json.dump(recent_articles, f, ensure_ascii=False, indent=2)

# Genera HTML automatico per index.html
html_content = ""
for art in recent_articles:
    html_content += f"""
    <article>
      <div class='title'>{art['title_it']}</div>
      <div class='date'>{art['published']}</div>
      <a href='{art['link']}' target='_blank'>Leggi / Watch</a>
    </article>
    """

# Aggiungi data ultimo aggiornamento
now = datetime.now().strftime("%d/%m/%Y %H:%M")
html_content += f"""
  <p style='text-align:center; margin-top:30px; font-size:0.9em; color:#A9CCE3;'>
    🕒 Ultimo aggiornamento: {now}
  </p>
"""

# Inserisci gli articoli nel template HTML
with open("index.html", "r", encoding="utf-8") as f:
    template = f.read()

template = template.replace(
    "<!-- Gli articoli saranno generati automaticamente dallo script Python -->",
    html_content
)

# Salva il nuovo file HTML
with open("index.html", "w", encoding="utf-8") as f:
    f.write(template)
