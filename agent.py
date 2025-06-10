import schedule
import time
import random
import argparse
import os
import tweepy

from post_generator import PostGenerator
from twitter_poster import post_to_x, check_mentions_and_reply, interact_with_target_user
from news_reader import get_random_football_headline

parser = argparse.ArgumentParser(description="Uruchamia autonomicznego agenta AI 'Andrzej' na Twitterze.")
parser.add_argument('--post-now', action='store_true', help="Publikuje jednego posta natychmiast po uruchomieniu agenta.")
args = parser.parse_args()

generator = PostGenerator()

def run_agent_cycle():
    """Główny cykl myślowy agenta, teraz z lepszym logowaniem."""
    print("\n--- Nowy cykl myślowy agenta ---")
    
    action = random.choice(['spontaneous_post', 'comment_news'])
    post_text = None

    try:
        if action == 'spontaneous_post':
            print("    - Decyzja: Piszę spontaniczny post.")
            post_text = generator.generate_spontaneous_post()
        
        elif action == 'comment_news':
            print("    - Decyzja: Komentuję newsa piłkarskiego.")
            headline = get_random_football_headline()
            if headline:
                print(f"    - Wylosowany nagłówek: '{headline}'")
                post_text = generator.generate_comment_on_news(headline)
            else:
                print("    - Nie udało się pobrać newsa, odpuszczam w tym cyklu.")
        
        if post_text and "my brain is broken" not in post_text:
            print(f"✍️  Andrzej wymyślił: '{post_text}'")
            post_to_x(post_text)
        else:
            print("🛑 Nie wygenerowano tekstu do publikacji w tym cyklu.")
            
    except Exception as e:
        print(f"❌ Wystąpił krytyczny błąd w cyklu agenta: {e}")


def run_interaction_cycle():
    """Cykl sprawdzania interakcji (wzmianek)."""
    try:
        check_mentions_and_reply(generator)
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas sprawdzania wzmianek: {e}")

def run_fan_cycle(targets: list):
    """Wybiera losowy cel z listy i sprawdza jego aktywność."""
    if not targets:
        return
    chosen_target = random.choice(targets)
    try:
        interact_with_target_user(chosen_target)
    except Exception as e:
        print(f"❌ Wystąpił krytyczny błąd w cyklu fana dla celu {chosen_target}: {e}")

def load_targets(filename="targets.txt") -> list:
    """Wczytuje listę nazw użytkowników z pliku tekstowego."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if targets:
                print(f"✅ Pomyślnie wczytano {len(targets)} celów z pliku {filename}.")
            else:
                print(f"⚠️ Plik {filename} jest pusty lub zawiera tylko komentarze. Moduł fana nie będzie aktywny.")
            return targets
    except FileNotFoundError:
        print(f"❌ Nie znaleziono pliku {filename}. Moduł fana nie będzie aktywny.")
        return []


fan_targets = load_targets()

losowy_interwal = random.randint(60, 120)
print(f"🤖 Agent Andrzeja uruchomiony. Publikowanie postów co ~{losowy_interwal} minut.")
schedule.every(losowy_interwal).minutes.do(run_agent_cycle)

print("👂 Nasłuchiwanie wzmianek co 15 minut.")
schedule.every(15).minutes.do(run_interaction_cycle)

if fan_targets:
    fan_interval = random.randint(3, 7)
    print(f"❤️  Aktywność fana zaplanowana co ~{fan_interval} godzin.")
    schedule.every(fan_interval).hours.do(run_fan_cycle, targets=fan_targets)

print("\n--- Sprawdzam, czy ktoś pisał do Andrzeja, gdy spał... ---")
run_interaction_cycle()

if args.post_now:
    print("\n--- Użytkownik zażądał natychmiastowej publikacji (--post-now)... ---")
    run_agent_cycle()
else:
    print("\n--- Agent uruchomiony w trybie standardowym. Czeka na pierwszy zaplanowany cykl... ---")

print("\n✅ Agent jest w pełni operacyjny. Wchodzę w tryb pętli.")
while True:
    schedule.run_pending()
    time.sleep(1)