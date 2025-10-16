import feedparser
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# --- Configurazione Corretta ---
URL_FEED_AZZURRA = "https://www.fonteazzurra.it/feed/"
FALLBACK_URL = "https://sscnapoli.it/news/" # <--- NUOVO URL DI FALLBACK SU /news/
MAX_ARTICLES = 10
FEED_JSON_PATH = 'feed.json'
INDEX_HTML_PATH = 'index.html'

def parse_rss():
    """Tenta di analizzare il feed RSS di Fonte Azzurra."""
    print("🔵 Avvio aggiornamento Fonte Azzurra...")
    try:
        feed = feedparser.parse(URL_FEED_AZZURRA)
        entries = []
        for entry in feed.entries[:MAX_ARTICLES]:
            # Rimuove eventuali tag HTML dal titolo e lo pulisce
            title = BeautifulSoup(entry.title, 'html.parser').get_text().strip()
            date_str = getattr(entry, 'published', getattr(entry, 'updated', ''))
            
            if date_str:
                try:
                    date_obj = datetime(*entry.published_parsed[:6])
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                except Exception:
                    formatted_date = ""
            else:
                formatted_date = ""

            entries.append({
                'title': title,
                'link': entry.link,
                'date': formatted_date,
                'source': 'Fonte Azzurra'
            })
        
        if entries:
            print(f"✅ Estratti {len(entries)} articoli da Fonte Azzurra.")
            return entries
        
        print("⚠️ Nessun articolo trovato nel feed RSS. Passaggio al fallback.")
        return None

    except Exception as e:
        print(f"❌ Errore nel parsing RSS: {e}")
        print("Passaggio al fallback.")
        return None

def scraping_fallback():
    """Esegue lo scraping degli articoli dal sito SSC Napoli (fallback)."""
    print(f"🧩 Fallback attivo: estraggo articoli dal sito SSC Napoli da {FALLBACK_URL}...")
    articles = []
    
    try:
        # Aggiungo un header User-Agent per rendere la richiesta più simile a un browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(FALLBACK_URL, headers=headers)
        response.raise_for_status() # Solleva un'eccezione per errori HTTP
        soup = BeautifulSoup(response.content, 'html.parser')

        # Selettore ancora più generale per trovare i contenitori degli articoli
        # Si assume che gli articoli siano in un <div> o <article> che ha una classe
        article_containers = soup.find_all(
            ['div', 'article'], 
            class_=re.compile(r'comunicati-item|article-item|news-item|post')
        )
        
        if not article_containers:
            print("❌ Errore nello scraping: Nessun contenitore articolo trovato con selettori comuni.")
            return articles

        for item in article_containers[:MAX_ARTICLES]:
            a_tag = item.find('a', href=True) # Cerca un tag <a> con un attributo href valido
            if not a_tag:
                continue
            
            link = a_tag['href']
            
            # Ricerca flessibile del titolo (H2, H3, H5 o span)
            title_tag = item.find(['h2', 'h3', 'h5', 'span'], class_=re.compile(r'com-title|title|post-title|news-title'))
            title = title_tag.get_text().strip() if title_tag else "Senza titolo"
            
            # Ricerca flessibile della data
            date_tag = item.find(['span', 'p'], class_=re.compile(r'com-data|date|article-date|post-date'))
            date_str = date_tag.get_text().strip() if date_tag else ""
            
            # Estrazione del formato data gg/mm/aaaa
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_str)
            formatted_date = date_match.group(0) if date_match else ""

            articles.append({
                'title': title,
                'link': link,
                'date': formatted_date,
                'source': 'SSC Napoli (Fallback)'
            })

        print(f"✅ Estratti {len(articles)} articoli:")
        for article in articles:
            print(f"- {article['title']} ({article['link']})")
            
        return articles

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore nella richiesta HTTP durante il fallback: {e}")
    except Exception as e:
        print(f"❌ Errore generico nello scraping: {e}")
        
    return articles

def save_to_json(data):
    """Salva i dati estratti nel file JSON."""
    try:
        with open(FEED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"📝 Dati salvati con successo in {FEED_JSON_PATH}")
    except Exception as e:
        print(f"❌ Errore nel salvataggio del JSON: {e}")

def update_index_html(articles):
    """Aggiorna la sezione dei contenuti dinamici nel file index.html."""
    
    try:
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Errore: {INDEX_HTML_PATH} non trovato. Impossibile aggiornare.")
        return

    new_content_html = ""
    for article in articles:
        new_content_html += f'<li><a href="{article["link"]}" target="_blank">{article["title"]}</a> <small>({article["date"]})</small></li>\n'
    
    new_content_html = new_content_html.strip()

    start_tag = ''
    end_tag = ''

    if start_tag not in content or end_tag not in content:
        print("⚠️ Attenzione: I tag di sostituzione dinamica non sono presenti in index.html.")
        return

    replacement_block = f'{start_tag}\n{new_content_html}\n{end_tag}'
    
    updated_content = re.sub(
        r'.*?', 
        replacement_block, 
        content, 
        flags=re.DOTALL
    )

    try:
        with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"📝 {INDEX_HTML_PATH} aggiornato con successo.")
    except Exception as e:
        print(f"❌ Errore nella scrittura di {INDEX_HTML_PATH}: {e}")

def main():
    """Funzione principale per l'esecuzione."""
    
    articles = parse_rss()
    
    if not articles:
        articles = scraping_fallback()

    if articles:
        save_to_json(articles)
        update_index_html(articles)
    else:
        print("🔴 Nessun articolo estratto. I file non saranno modificati.")


if __name__ == "__main__":
    main()
