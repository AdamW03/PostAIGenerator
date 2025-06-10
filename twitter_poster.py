# twitter_poster.py
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

def get_twitter_client():
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    return client

def post_to_x(text: str):
    if not all([os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"), os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET")]):
        print("🛑 Twitter API keys not found in .env file. Skipping post.")
        return

    client = get_twitter_client()
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Successfully posted to X: {response.data['id']}")
    except Exception as e:
        print(f"❌ Error posting to X: {e}")

# Przykład użycia
if __name__ == '__main__':
    post_to_x("aba daba")