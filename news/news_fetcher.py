import feedparser
from datetime import datetime
from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI.strip())
db = client["cyberbot"]
news_collection = db["news"]

# RSS FEEDS (FREE & RELIABLE)
RSS_FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "CERT-IN": "https://www.cert-in.org.in/rss.xml"
}

def fetch_and_store_news():
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:  # limit per source
            news_item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "source": source,
                "published": entry.get("published", ""),
                "timestamp": datetime.utcnow()
            }

            # Avoid duplicates
            if not news_collection.find_one({"link": news_item["link"]}):
                news_collection.insert_one(news_item)

    return True
