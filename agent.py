# agent.py
import schedule
import time
import random
import argparse  # KROK 1: Dodajemy import

# Importujemy nasze własne moduły
from post_generator import PostGenerator
from twitter_poster import post_to_x, check_mentions_and_reply

# --- KROK 2: Definiowanie i parsowanie argumentów wiersza poleceń ---
parser = argparse.ArgumentParser(description="Uruchamia autonomicznego agenta AI 'Andrzej' na Twitterze.")
parser.add_argument(
    '--post-now',
    action='store_true',  # To sprawia, że argument działa jak przełącznik (flaga)
    help="Publikuje jednego posta natychmiast po uruchomieniu agenta."
)
args = parser.parse_args()


# --- Definicje funkcji (bez zmian) ---
generator = PostGenerator()

def run_agent_cycle():
    """Główne zadanie agenta: wymyśl coś, stwórz posta i opublikuj."""
    print("\n--- Nowy cykl myślowy agenta ---")
    try:
        post_text = generator.generate_spontaneous_post()
        print(f"✍️  Andrzej wymyślił: '{post_text}'")
        if post_text and "mózg mi się zepsuł" not in post_text:
            print("Próba publikacji na X...")
            post_to_x(post_text)
        else:
            print("🛑 Post był pusty lub zawierał błąd. Pomijam publikację w tym cyklu.")
    except Exception as e:
        print(f"❌ Wystąpił krytyczny błąd w cyklu agenta: {e}")

def run_interaction_cycle():
    """Cykl sprawdzania interakcji (wzmianek)."""
    try:
        check_mentions_and_reply(generator)
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas sprawdzania wzmianek: {e}")


# --- Konfiguracja Harmonogramu (bez zmian) ---
losowy_interwal = random.randint(60, 120)
print(f"🤖 Agent Andrzeja uruchomiony. Publikowanie postów co ~{losowy_interwal} minut.")
schedule.every(losowy_interwal).minutes.do(run_agent_cycle)

print("👂 Nasłuchiwanie wzmianek co 15 minut.")
schedule.every(15).minutes.do(run_interaction_cycle)


# --- KROK 3: Zmodyfikowana logika startowa ---
print("\n--- Sprawdzam, czy ktoś pisał do Andrzeja, gdy spał... ---")
run_interaction_cycle()

# Sprawdzamy, czy użytkownik użył flagi --post-now
if args.post_now:
    print("\n--- Użytkownik zażądał natychmiastowej publikacji (--post-now)... ---")
    run_agent_cycle()
else:
    print("\n--- Agent uruchomiony w trybie standardowym. Czeka na pierwszy zaplanowany cykl... ---")


# --- Główna Pętla Agenta (bez zmian) ---
print("\n✅ Agent jest w pełni operacyjny. Wchodzę w tryb pętli.")
while True:
    schedule.run_pending()
    time.sleep(1)