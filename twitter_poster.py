# twitter_poster.py
import tweepy
import os
from dotenv import load_dotenv
import time

load_dotenv()
SINCE_ID_FILE = "since_id.txt"

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

def read_since_id():
    """Odczytuje ID ostatnio obsłużonego tweeta z pliku."""
    try:
        with open(SINCE_ID_FILE, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None  # Zwraca None, jeśli plik nie istnieje (przy pierwszym uruchomieniu)

def write_since_id(tweet_id):
    """Zapisuje ID ostatnio obsłużonego tweeta do pliku."""
    with open(SINCE_ID_FILE, "w") as f:
        f.write(str(tweet_id))

def check_mentions_and_reply(generator_instance):
    """
    Wyszukuje tweety wspominające o bocie i zleca generatorowi stworzenie odpowiedzi.
    Używa publicznego wyszukiwania, aby uniknąć problemów z uprawnieniami.
    """
    print("🕵️  Wyszukuję nowe wzmianki o bocie...")
    client = get_twitter_client()
    my_username = client.get_me().data.username
    since_id = read_since_id()

    # Tworzymy zapytanie wyszukiwania: szukaj tweetów zawierających naszą nazwę,
    # które nie są naszymi własnymi tweetami (żeby nie odpowiadać samemu sobie).
    query = f"@{my_username} -is:retweet -from:{my_username}"

    # Używamy metody search_recent_tweets zamiast get_users_mentions
    response = client.search_recent_tweets(
        query=query,
        since_id=since_id,
        expansions=["author_id"],
        tweet_fields=["text"],
        user_auth=True
    )

    if not response.data:
        print("Brak nowych wzmianek.")
        return

    newest_id = response.meta['newest_id']

    for mention in reversed(response.data):
        print(f"    - Znaleziono wzmiankę od ID {mention.author_id}: '{mention.text}'")
        
        # Usuwamy własną nazwę użytkownika z tekstu, żeby nie "czytał" jej na głos
        cleaned_text = mention.text.replace(f"@{my_username}", "").strip()
        reply_prompt = f"Ktoś napisał do ciebie: '{cleaned_text}'. Odpowiedz krótko w swoim stylu."
        
        reply_text = generator_instance.generate(reply_prompt)
        
        print(f"    - 🤖 Andrzej odpowiada: '{reply_text}'")
        
        # Publikujemy odpowiedź bezpośrednio na tweeta
        client.create_tweet(text=reply_text, in_reply_to_tweet_id=mention.id)
        time.sleep(5)

    write_since_id(newest_id)
# Przykład użycia
if __name__ == '__main__':
    post_to_x("aba daba")