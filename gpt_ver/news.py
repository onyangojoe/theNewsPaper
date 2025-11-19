# Flask Kenyan Politics News Project

Below is the **full multi‑file Flask project structure**, including:
- `app.py` (main application)
- `scraper.py` (political news scraper)
- `templates/` folder with HTML templates
- `static/` folder
- **Admin login system** (username + password)
- `Dockerfile`

---

## 📁 Project Structure
```
kenya_politics_news/
│
├── app.py
├── scraper.py
├── requirements.txt
├── Dockerfile
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│
└── static/
    └── styles.css
```

---

## 🧠 `scraper.py`
```python
import feedparser
from datetime import datetime

RSS_FEEDS = [
    "https://www.standardmedia.co.ke/rss/kenya_politics.xml",
    "https://www.the-star.co.ke/feed/category/politics/",
    "https://nation.africa/kenya/news/politics/rss",
]

def scrape_political_news():
    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if "politic" not in entry.title.lower():
                continue

            articles.append({
                "title": entry.title,
                "summary": entry.summary[:400] + "...",
                "link": entry.link,
                "published": entry.get("published", str(datetime.now())),
            })

    return articles[:5]  # return 5 latest
```

---

## 🧩 `app.py`
```python
from flask import Flask, render_template, request, redirect, session, url_for
from scraper import scrape_political_news
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mysecret")
app.permanent_session_lifetime = timedelta(hours=3)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "changeme"

ARTICLES_CACHE = []

@app.route("/")
def index():
    global ARTICLES_CACHE
    ARTICLES_CACHE = scrape_political_news()
    return render_template("index.html", articles=ARTICLES_CACHE)

# ---------------------- ADMIN LOGIN ----------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template("admin_login.html", error="Invalid login")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template("admin_dashboard.html", articles=ARTICLES_CACHE)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# ----------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

---

## 🎨 `templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kenya Politics News</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <header>
        <h1>Kenya Political News</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin">Admin</a>
        </nav>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

---

## 📰 `templates/index.html`
```html
{% extends "base.html" %}
{% block content %}
<h2>Latest Political News</h2>

{% for article in articles %}
<div class="article-card">
    <h3>{{ article.title }}</h3>
    <p>{{ article.summary }}</p>
    <a href="{{ article.link }}" target="_blank">Soma zaidi</a>
</div>
{% endfor %}

{% endblock %}
```

---

## 🔐 `templates/admin_login.html`
```html
{% extends "base.html" %}
{% block content %}
<h2>Admin Login</h2>

<form method="POST">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>

{% if error %}<p class="error">{{ error }}</p>{% endif %}

{% endblock %}
```

---

## 🛠️ `templates/admin_dashboard.html`
```html
{% extends "base.html" %}
{% block content %}
<h2>Admin Dashboard</h2>
<p>Logged in as admin.</p>

<h3>Current Articles Scraped</h3>
<ul>
    {% for a in articles %}
        <li><strong>{{ a.title }}</strong> – {{ a.published }}</li>
    {% endfor %}
</ul>

<a href="/admin/logout">Logout</a>

{% endblock %}
```

---

## 🎨 `static/styles.css`
```css
body {
    font-family: Arial;
    margin: 0;
    background: #f5f5f5;
}
header {
    background: #202a44;
    color: white;
    padding: 20px;
    display: flex;
    justify-content: space-between;
}
nav a {
    color: white;
    margin-left: 10px;
    text-decoration: none;
}
.article-card {
    background: white;
    margin: 20px;
    padding: 15px;
    border-radius: 8px;
}
```

---

## 🐳 Dockerfile
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

---

If you want, I can also add:
✅ Database support (SQLite/PostgreSQL)  
✅ Article saving + admin editor  
✅ Automated cron‑jobs / scheduler for scraping  
✅ Full Swahili translation of all text
