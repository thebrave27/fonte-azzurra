import feedparser
import json
from datetime import datetime

# Feed ufficiali SSC Napoli
feeds = {
    "comunicati": "https://www.sscnapoli.it/category/comunicati-stampa/feed/",
    "youtube": "https://www.youtube.com/feeds/videos.xml?channel_id=UCsYjM4I1zogVxZtkvOSN49A",
    "radio": "https://www.radiokisskiss.it/feed/"
}

articles = []

for key, url in feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        articles.append({
            "title_it": entry.title,
            "title_en": entry.title,  # puoi aggiungere traduzione manuale se vuoi
            "link": entry.link,
            "published": entry.published if 'published' in entry else str(datetime.now()),
            "source": key
        })

# Salva feed JSON per Zapier/Make
with open("site/feed.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

# Genera HTML automatico per site/index.html
html_content = ""
for art in articles:
    html_content += f"""
    <article>
      <div class='title'>{art['title_it']}</div>
      <div class='date'>{art['published']}</div>
      <a href='{art['link']}' target='_blank'>Leggi / Watch</a>
    </article>
    """

with open("site/index.html", "r", encoding="utf-8") as f:
    template = f.read()

template = template.replace("<!-- Gli articoli saranno generati automaticamente dallo script Python -->", html_content)

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(template)
