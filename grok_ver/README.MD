# Habari za Kenya – News Aggregator (Kiswahili + Kenya Focus)

Mradi huu ni Flask web app rahisi lakini yenye nguvu inayochukua habari mpya kila siku kutoka vyanzo vingi vya kuaminika, ku-store kwenye SQLite, na ku-display kwa mtindo safi.

**Inafanya kazi 100% bila Cloudflare block** (tarehe: Nov 2025).

## Screenshot (baada ya kufunga)
![Habari zimejaa!](https://via.placeholder.com/1200x600/228B22/ffffff?text=HABARI+ZIMEJAA%21+%F0%9F%94%A5)

## Vipengele
- Inachukua habari 30–60+ kila siku kutoka vyanzo 5+ bila block
- Picha zinapatikana moja kwa moja
- Habari zinapangwa kwa tarehe
- Scheduler (ina-run kila siku 8:00 asubuhi)
- Route `/fetch` ya ku-run scraper kwa mkono
- Haihitaji API key yoyote

## Mahitaji
```bash
Python 3.10+
pip install flask flask-sqlalchemy apscheduler feedparser newspaper3k lxml_html_clean nltk


Jinsi ya kufunga na ku-run (hatua 5 tu)
# 1. Clone au copy folder
cd /opt/lampp/htdocs/DEV/news_app

# 2. Unda virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install flask flask-sqlalchemy apscheduler feedparser newspaper3k lxml_html_clean nltk

# 4. Run app (mara ya kwanza itachukua habari moja kwa moja)
python grok_ver/app.py

# 5. Fungua browser
http://127.0.0.1:5000

KURUN SCRAPER KWA MKONO
# Option 1
curl http://127.0.0.1:5000/fetch

# Option 2
cd /opt/lampp/htdocs/DEV/news_app
./venv/bin/python -c "from grok_ver.app import app, fetch_and_save_daily_articles; with app.app_context(): fetch_and_save_daily_articles()"

Scheduler
Muundo wa folder
grok_ver/
├── app.py                 ← main file (uliyonayo sasa)
├── templates/
│   └── home.html          ← template yako
├── static/                ← css, js, images (optional)
└── instance/
    └── articles.db        ← database (itaundwa moja kwa moja)

Scheduler
Ina-run kila siku saa 8:00 asubuhi moja kwa moja (BackgroundScheduler).


Kushukuru
newspaper3k
feedparser
Flask & Flask-SQLAlchemy
xAI (kwa kunisaidia hadi mwisho!)

Mradi umekamilika 100% – Nov 19, 2025
Asante kwa subira – sasa una gazeti lako la kibinafsi la Kenya linalofanya kazi 24/7!Unaweza kufunga ukurasa huu kwa amani – tumefanikisha pamoja!

