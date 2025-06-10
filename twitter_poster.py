import tweepy
import os
from dotenv import load_dotenv
import time
import random
import json

load_dotenv()

# Pliki do śledzenia postępu
SINCE_ID_FILE = "since_id.txt"
FAN_SINCE_IDS_JSON_FILE = "fan_since_ids.json"

def get_twitter_client():
    """Tworzy i zwraca uwierzytelnionego klienta Tweepy."""
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    return client

def post_to_x(text: str):
    """Publikuje podany tekst jako nowy tweet."""
    client = get_twitter_client()
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Successfully posted to X: {response.data['id']}")
    except Exception as e:
        print(f"❌ Error posting to X: {e}")

def read_since_id(filename: str):
    """Odczytuje ID ostatnio obsłużonego tweeta z podanego pliku."""
    try:
        with open(filename, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None

def write_since_id(tweet_id, filename: str):
    """Zapisuje ID ostatnio obsłużonego tweeta do podanego pliku."""
    with open(filename, "w") as f:
        f.write(str(tweet_id))

def check_mentions_and_reply(generator_instance):
    """Wyszukuje wzmianki o bocie i zleca generatorowi stworzenie odpowiedzi."""
    print("🕵️  Wyszukuję nowe wzmianki o bocie...")
    client = get_twitter_client()
    my_username = client.get_me().data.username
    since_id = read_since_id(SINCE_ID_FILE)
    query = f"@{my_username} -is:retweet -from:{my_username}"
    try:
        response = client.search_recent_tweets(
            query=query, since_id=since_id, expansions=["author_id"],
            tweet_fields=["text"], user_auth=True
        )
    except tweepy.errors.TooManyRequests:
        print("    - ⚠️ Osiągnięto limit zapytań do API (429). Spróbuję ponownie w następnym cyklu.")
        return
    except Exception as e:
        print(f"    - ❌ Wystąpił nieoczekiwany błąd podczas wyszukiwania wzmianek: {e}")
        return
    if not response.data:
        print("    - Brak nowych wzmianek.")
        return
    newest_id = response.meta['newest_id']
    for mention in reversed(response.data):
        print(f"    - Znaleziono wzmiankę od ID {mention.author_id}: '{mention.text}'")
        cleaned_text = mention.text.replace(f"@{my_username}", "").strip()
        reply_prompt = f"Ktoś napisał do ciebie: '{cleaned_text}'. Odpowiedz krótko w swoim stylu."
        reply_text = generator_instance.generate(reply_prompt)
        print(f"    - 🤖 Andrzej odpowiada: '{reply_text}'")
        client.create_tweet(text=reply_text, in_reply_to_tweet_id=mention.id)
        time.sleep(5)
    write_since_id(newest_id, SINCE_ID_FILE)

def read_fan_since_id(username: str) -> int | None:
    """Odczytuje ID ostatniego tweeta dla konkretnego użytkownika z pliku JSON."""
    try:
        with open(FAN_SINCE_IDS_JSON_FILE, 'r') as f:
            data = json.load(f)
            return data.get(username)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def write_fan_since_id(username: str, tweet_id: int):
    """Zapisuje ID ostatniego tweeta dla konkretnego użytkownika do pliku JSON."""
    data = {}
    try:
        with open(FAN_SINCE_IDS_JSON_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    data[username] = tweet_id
    with open(FAN_SINCE_IDS_JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def interact_with_target_user(target_username: str):
    """Sprawdza ostatnie tweety docelowego użytkownika i losowo wchodzi z nimi w interakcję."""
    print(f"❤️  Sprawdzam aktywność ulubionego użytkownika: @{target_username}...")
    client = get_twitter_client()
    try:
        user_response = client.get_user(username=target_username, user_auth=True)
        if not user_response.data:
            print(f"    - ❌ Nie znaleziono użytkownika @{target_username}. Pomijam.")
            return
        target_user_id = user_response.data.id
        since_id = read_fan_since_id(target_username)
        response = client.get_users_tweets(
            id=target_user_id, since_id=since_id, max_results=5,
            exclude=["replies", "retweets"], user_auth=True
        )
    except tweepy.errors.TooManyRequests:
        print("    - ⚠️ Osiągnięto limit zapytań do API (429). Spróbuję ponownie w następnym cyklu.")
        return
    except Exception as e:
        print(f"    - ❌ Wystąpił nieoczekiwany błąd podczas pobierania tweetów fana: {e}")
        return
        
    if not response.data:
        print(f"    - @{target_username} nie ma nowej aktywności do sprawdzenia.")
        return
        
    newest_id = response.meta['newest_id']
    write_fan_since_id(target_username, newest_id)
    
    tweet_to_consider = random.choice(response.data)
    print(f"    - Rozważam interakcję z tweetem: '{tweet_to_consider.text[:40]}...'")
    
    if random.random() < 0.74:
        action = random.choice(['like', 'retweet'])
        try:
            if action == 'like':
                print(f"    - -> Postanowiłem polubić ten tweet!")
                client.like(tweet_to_consider.id)
            elif action == 'retweet':
                print(f"    - -> Postanowiłem zretweetować ten post!")
                client.retweet(tweet_to_consider.id)
            print("    - ✅ Akcja fana wykonana pomyślnie.")
        except Exception as e:
            print(f"    - ❌ Błąd podczas wykonywania akcji fana: {e}")
    else:
        print("    - -> Tym razem odpuszczam. Bez interakcji.")
