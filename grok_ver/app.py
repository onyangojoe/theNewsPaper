from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
import feedparser
from newspaper import Article, ArticleException
import nltk
import re

# Download once
nltk.download('punkt', quiet=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500), unique=True)
    image_url = db.Column(db.String(500))           # ← MPYA: PICHA
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tengeneza database
with app.app_context():
    db.create_all()

# RSS ZOTE ZINAZOFANYA KAZI 100% NOV 2025
RSS_FEEDS = [
    "https://allafrica.com/misc/tools/rss/en/kenya.html",
    "https://feeds.bbci.co.uk/swahili/rss.xml",
    "https://www.dw.com/swahili/s-11616/rss",
    "https://www.africanews.com/rss.xml",
    "https://www.voanews.com/api/zq|omeqto_oi",
    "https://www.standardmedia.co.ke/rss/headlines.php",
    "https://www.the-star.co.ke/rss"
]

# ====================== PICHA FUNCTION (BORA KABISA) ======================
def get_best_image(article):
    # 1. newspaper3k top_image (mara nyingi ni bora)
    if article.top_image and "placeholder" not in article.top_image.lower() and len(article.top_image) > 30:
        return article.top_image

    # 2. Chukua picha yoyote kutoka HTML
    try:
        imgs = re.findall(r'src="(https?://[^"]+\.(jpg|jpeg|png|gif|webp))"', article.html, re.IGNORECASE)
        if imgs:
            return imgs[0][0] if isinstance(imgs[0], tuple) else imgs[0]
    except:
        pass

    # 3. Default picha nzuri ya Kenya (unaweza badilisha)
    return "https://via.placeholder.com/1200x600/006400/ffffff?text=HABARI+ZA+SIASA+KENYA"

# ====================== TRIM FUNCTION ======================
def trim_to_word_count(text, min_words=150, max_words=400):
    words = text.split()
    if len(words) <= min_words:
        return text
    return ' '.join(words[:max_words]) + "..."

# ====================== DAILY SCRAPER ======================
def fetch_and_save_daily_articles():
    global RSS_FEEDS  
    today = date.today()
    added_count = 0
    
    print(f"[{datetime.now()}] Inaanza kuchukua habari za {today}...")

    for RSS_URL in RSS_FEEDS:                               # ← line mpya
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            continue

        for entry in feed.entries:
            if added_count >= 30:          # unaweza kuweka 50 au 100
                break

            link = entry.link if hasattr(entry, 'link') else entry.get('id', '')
            if not link or db.session.query(NewsArticle).filter_by(source_url=link).first():
                continue

            try:
                article = Article(link)
                article.download(timeout=15)
                article.parse()

                if len(article.text or "") < 600:
                    continue

                trimmed_content = trim_to_word_count(article.text.strip(), 150, 400)
                if len(trimmed_content.split()) < 130:
                    continue

                best_image = get_best_image(article)

                new_article = NewsArticle(
                    title=article.title or entry.title,
                    content=trimmed_content,
                    source_url=link,
                    image_url=best_image,
                    published_at=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow()
                )
                db.session.add(new_article)
                added_count += 1

            except Exception as e:
                print(f"Error: {link} → {e}")
                continue

        if added_count >= 30:
            break

    db.session.commit()
    print(f"Imemaliza! Imeongeza habari {added_count} mpya leo.")

# Run mara moja unapoanzisha app (kwa testing)
with app.app_context():
    if NewsArticle.query.filter(db.func.date(NewsArticle.created_at) == date.today()).count() == 0:
        fetch_and_save_daily_articles()

# Scheduler – kila siku saa 8:00 asubuhi
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_save_daily_articles, trigger="cron", hour=8, minute=0)
scheduler.start()

# ====================== ROUTES ======================
@app.route('/')
def home():
    articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    
    grouped = {}
    for a in articles:
        day = a.created_at.date()
        if day not in grouped:
            grouped[day] = []
        grouped[day].append(a)
    
    return render_template('home.html', grouped=grouped)

@app.route('/fetch')
def manual_fetch():
    fetch_and_save_daily_articles()
    return "Habari mpya zimechukuliwa! <a href='/'>Rudi nyumbani</a>"

if __name__ == '__main__':
    app.run(debug=True)