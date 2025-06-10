import feedparser
import random

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/sport/football/rss.xml"
]

def get_random_football_headline():
    """Pobiera losowy nagłówek z jednego z kanałów RSS."""
    try:
        feed_url = random.choice(RSS_FEEDS)
        print(f"Fetching news from: {feed_url}") 
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            print("    - RSS feed is empty or there was an error.")
            return None
            
        random_entry = random.choice(feed.entries)
        clean_title = random_entry.title.split(' - ')[0]
        return clean_title
        
    except Exception as e:
        print(f"❌ Error fetching RSS news: {e}") 
        return None

if __name__ == '__main__':
    print("Testing news reader...")
    headline = get_random_football_headline()
    if headline:
        print(f"Successfully fetched headline: '{headline}'")
    else:
        print("Failed to fetch headline.")