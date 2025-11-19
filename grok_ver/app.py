from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
import feedparser
from newspaper import Article, ArticleException
import nltk

# Download nltk data once (required by newspaper3k)
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
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create DB if not exists
with app.app_context():
    db.create_all()

def trim_to_word_count(text, min_words=180, max_words=350):
    words = text.split()
    if len(words) < min_words:
        return text  # kama ni fupi sana, tumia yote
    elif len(words) > max_words:
        return ' '.join(words[:max_words]) + 30]) + "..."  # +30 ili iishe vizuri
    return text

def fetch_and_save_daily_articles():
    RSS_URL = "https://news.google.com/rss/search?q=siasa+kenya+OR+ruto+OR+raila+OR+azimio+OR+%22kenya+kwanza%22+OR+bunge&hl=sw&gl=KE&ceid=KE:sw&scoring=n"
    
    feed = feedparser.parse(RSS_URL)
    
    today = date.today()
    added_count = 0
    
    print(f"[{datetime.now()}] Starting daily fetch for {today}...")
    
    for entry in feed.entries:
        if added_count >= 5:
            break
            
        # Skip if already in DB
        if db.session.query(NewsArticle).filter_by(source_url=entry.link).first():
            continue
            
        try:
            article = Article(entry.link)
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 600:  # skip too short/empty
                continue
                
            clean_text = article.text.strip()
            trimmed_content = trim_to_word_count(clean_text, 180, 350)
            
            if len(trimmed_content.split()) < 150:  # still too short after trim
                continue
                
            new_article = NewsArticle(
                title=article.title or entry.title,
                content=trimmed_content,
                source_url=entry.link,
                published_at=datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else datetime.utcnow()
            )
            db.session.add(new_article)
            added_count += 1
            
        except ArticleException as e:
            print(f"Error downloading {entry.link}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error {entry.link}: {e}")
            continue
    
    db.session.commit()
    print(f"Added {added_count} new articles for {today}")

# Run fetch immediately on startup if no articles today
with app.app_context():
    today_articles = NewsArticle.query.filter(db.func.date(NewsArticle.created_at) == date.today()).count()
    if today_articles == 0:
        fetch_and_save_daily_articles()

# Scheduler – kila siku saa 8 asubuhi (unaweza badilisha)
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_save_daily_articles, trigger="cron", hour=8, minute=0)
scheduler.start()

@app.route('/')
def home():
    # Onyesha articles za leo kwanza, kisha za nyuma
    articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    
    # Group by date
    grouped = {}
    for a in articles:
        day = a.created_at.date() if a.created_at else date.today()
        if day not in grouped:
            grouped[day] = []
        grouped[day].append(a)
    
    return render_template('home.html', grouped=grouped)

# Optional manual trigger (kwa testing)
@app.route('/fetch')
def manual_fetch():
    fetch_and_save_daily_articles()
    return "Fetch completed! <a href='/'>Go home</a>"

if __name__ == '__main__':
    app.run(debug=True)