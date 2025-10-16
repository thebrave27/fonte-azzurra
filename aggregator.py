import feedparser
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

# --- Configurazione ---
URL_FEED_AZZURRA = "https://www.fonteazzurra.it/feed/"
FALLBACK_URL = "https://sscnapoli.it/comunicati/"
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
            # Utilizza il campo 'published' o 'updated' per la data
            date_str = getattr(entry, 'published', getattr(entry, 'updated', ''))
            
            # Formattazione della data, se presente
            if date_str:
                try:
                    # Tenta di analizzare la data con feedparser
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
    """Esegue lo scraping dei comunicati dal sito SSC Napoli (fallback)."""
    print(f"🧩 Fallback attivo: estraggo comunicati dal sito SSC Napoli da {FALLBACK_URL}...")
    articles = []
    
    try:
        response = requests.get(FALLBACK_URL)
        response.raise_for_status() # Solleva un'eccezione per errori HTTP (4xx o 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

        # NUOVO SELETTORE: Trova tutti i div che contengono il comunicato.
        # Basato sull'analisi del sito web attuale. (Es. .comunicati-item)
        comunicati_list = soup.find_all('div', class_=re.compile(r'comunicati-item'))
        
        if not comunicati_list:
            print("❌ Errore nello scraping: Nessun elemento 'comunicati-item' trovato.")
            return articles

        for item in comunicati_list[:MAX_ARTICLES]:
            # Trova il link (il tag 'a' all'interno del comunicato)
            a_tag = item.find('a')
            if not a_tag or not a_tag.get('href'):
                continue
            
            link = a_tag['href']
            
            # NUOVO SELETTORE: Trova il titolo (spesso un h5)
            # Potrebbe essere necessario cercare un <h5> o <h2>, a seconda della struttura
            title_tag = item.find(['h2', 'h5', 'span'], class_=re.compile(r'com-title|title'))
            title = title_tag.get_text().strip() if title_tag else "Senza titolo"
            
            # NUOVO SELETTORE: Trova la data
            date_tag = item.find(['span', 'p'], class_=re.compile(r'com-data|date'))
            date_str = date_tag.get_text().strip() if date_tag else ""
            
            # Pulisce la data (es. "30/09/2024")
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_str)
            formatted_date = date_match.group(0) if date_match else ""

            articles.append({
                'title': title,
                'link': link,
                'date': formatted_date,
                'source': 'SSC Napoli (Fallback)'
            })

        print(f"✅ Estratti {len(articles)} comunicati:")
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
    
    # 1. Carica il contenuto attuale di index.html
    try:
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Errore: {INDEX_HTML_PATH} non trovato. Impossibile aggiornare.")
        return

    # 2. Prepara il nuovo contenuto HTML
    new_content_html = ""
    for article in articles:
        # Crea un elemento <li> pulito
        new_content_html += f'<li><a href="{article["link"]}" target="_blank">{article["title"]}</a> <small>({article["date"]})</small></li>\n'
    
    # Rimuove il newline finale
    new_content_html = new_content_html.strip()

    # 3. Trova e sostituisci il blocco dinamico
    start_tag = ''
    end_tag = ''

    if start_tag not in content or end_tag not in content:
        print("⚠️ Attenzione: I tag di sostituzione dinamica non sono presenti in index.html.")
        return

    # Crea il blocco completo con i tag
    replacement_block = f'{start_tag}\n{new_content_html}\n{end_tag}'
    
    # Usa un'espressione regolare per la sostituzione (inclusi tutti i contenuti tra i tag)
    # re.DOTALL permette all'espressione di attraversare le nuove righe
    updated_content = re.sub(
        r'.*?', 
        replacement_block, 
        content, 
        flags=re.DOTALL
    )

    # 4. Scrivi il contenuto aggiornato
    try:
        with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"📝 {INDEX_HTML_PATH} aggiornato con successo.")
    except Exception as e:
        print(f"❌ Errore nella scrittura di {INDEX_HTML_PATH}: {e}")

def main():
    """Funzione principale per l'esecuzione."""
    
    # Tenta prima il feed RSS
    articles = parse_rss()
    
    # Se il feed RSS fallisce o è vuoto, usa lo scraping di fallback
    if not articles:
        articles = scraping_fallback()

    if articles:
        save_to_json(articles)
        update_index_html(articles)
    else:
        print("🔴 Nessun articolo estratto. I file non saranno modificati.")


if __name__ == "__main__":
    main()
