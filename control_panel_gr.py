import gradio as gr
import threading
import time
import schedule
import random
import os
import io
import contextlib

from post_generator import PostGenerator
from twitter_poster import post_to_x, check_mentions_and_reply, interact_with_target_user
from news_reader import get_random_football_headline

agent_thread = None
stop_event = threading.Event()
generator = PostGenerator()


def load_targets_from_file(filename="targets.txt"):
    """Wczytuje cele z pliku do wyświetlenia w UI."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "# Plik targets.txt nie istnieje. Stwórz go i wpisz nazwy użytkowników."

def save_targets_to_file(targets_text, filename="targets.txt"):
    """Zapisuje cele z UI do pliku."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(targets_text)
    return f"Zapisano cele w {filename}"

def capture_output(func, *args, **kwargs):
    """Przechwytuje print() z funkcji i zwraca jako string."""
    str_io = io.StringIO()
    with contextlib.redirect_stdout(str_io):
        func(*args, **kwargs)
    return str_io.getvalue()


def run_agent_background_task(params):
    """Główna pętla agenta, która będzie działać w tle."""
    print("✅ Wątek agenta uruchomiony.")
    
    post_min, post_max = params['post_interval']
    mention_interval = params['mention_interval']
    fan_interval = params['fan_interval']
    targets = [line.strip() for line in params['targets_text'].splitlines() if line.strip() and not line.startswith('#')]

    schedule.clear() 
    schedule.every(random.randint(post_min, post_max)).minutes.do(run_agent_cycle)
    schedule.every(mention_interval).minutes.do(run_interaction_cycle)
    if targets:
        schedule.every(fan_interval).hours.do(run_fan_cycle, targets=targets)

    print("Harmonogram skonfigurowany. Agent rozpoczyna pracę w pętli...")
    
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)
    
    print("🛑 Wątek agenta otrzymał sygnał stop i kończy pracę.")


def run_agent_cycle():
    try:
        post_text = generator.generate_spontaneous_post()
        if post_text and "mózg mi się zepsuł" not in post_text:
            post_to_x(post_text)
        else:
            print("🛑 Post był pusty lub zawierał błąd. Pomijam publikację w tym cyklu.")
    except Exception as e:
        print(f"❌ Wystąpił krytyczny błąd w cyklu agenta: {e}")

def run_interaction_cycle():
    try:
        check_mentions_and_reply(generator)
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas sprawdzania wzmianek: {e}")

def run_fan_cycle(targets: list):
    if not targets: return
    chosen_target = random.choice(targets)
    try:
        interact_with_target_user(chosen_target)
    except Exception as e:
        print(f"❌ Wystąpił krytyczny błąd w cyklu fana dla celu {chosen_target}: {e}")


def start_agent(post_interval, mention_interval, fan_interval, targets_text):
    """Uruchamia agenta w osobnym wątku z parametrami z UI."""
    global agent_thread, stop_event
    if agent_thread and agent_thread.is_alive():
        return "Agent już działa w tle."

    save_targets_to_file(targets_text)
    
    stop_event.clear()
    
    post_min, post_max = int(post_interval[0]), int(post_interval[1])
    
    params = {
        'post_interval': (post_min, post_max),
        'mention_interval': mention_interval,
        'fan_interval': fan_interval,
        'targets_text': targets_text
    }
    agent_thread = threading.Thread(target=run_agent_background_task, args=(params,), daemon=True)
    agent_thread.start()
    return f"Agent uruchomiony!\n- Posty co {post_min}-{post_max} min\n- Wzmianki co {mention_interval} min\n- Akcja fana co {fan_interval} h"

def stop_agent():
    global agent_thread, stop_event
    if not agent_thread or not agent_thread.is_alive():
        return "Agent nie jest uruchomiony."
    
    stop_event.set()
    agent_thread.join(timeout=5) 
    return "Agent zatrzymany."

def force_post_wrapper():
    return capture_output(generator.generate_spontaneous_post_and_publish)

def force_mention_wrapper():
    return capture_output(run_interaction_cycle)

def force_fan_wrapper(targets_text):
    targets = [line.strip() for line in targets_text.splitlines() if line.strip() and not line.startswith('#')]
    if not targets:
        return "Brak celów na liście do wykonania akcji fana."
    return capture_output(run_fan_cycle, targets=targets)

def force_news_post_wrapper():
    """Wrapper do wymuszenia posta o newsie."""
    output_log = ""
    headline = get_random_football_headline()
    if headline:
        output_log += f"Wylosowany nagłówek: '{headline}'\n" + "-"*20 + "\n"
        output_log += capture_output(generator.generate_comment_on_news_and_publish, headline)
    else:
        output_log += "Nie udało się pobrać nagłówka wiadomości."
    return output_log

def force_random_action_wrapper():
    """Wrapper do wymuszenia losowej akcji, tak jak w cyklu autonomicznym."""
    
    action = random.choice(['spontaneous_post', 'comment_news'])
    
    if action == 'spontaneous_post':
        log_prefix = "Wylosowano akcję: Post Spontaniczny\n" + "-"*20 + "\n"
        return log_prefix + capture_output(generator.generate_spontaneous_post_and_publish)
    
    elif action == 'comment_news':
        log_prefix = "Wylosowano akcję: Post o Newsie\n" + "-"*20 + "\n"
        return log_prefix + force_news_post_wrapper() 


with gr.Blocks(theme=gr.themes.Soft(), title="Panel Kontrolny Agenta") as ui:
    gr.Markdown("# Panel Kontrolny Agenta 'Andrzej'")
    
    with gr.Row():
        start_button = gr.Button("✅ Uruchom Agenta", variant="primary")
        stop_button = gr.Button("🛑 Zatrzymaj Agenta", variant="stop")

    with gr.Accordion("Ustawienia Główne", open=False):
        gr.Markdown("Ustaw jak często agent ma wykonywać swoje podstawowe zadania.")
        post_interval_slider = gr.Slider(
            label="Interwał publikowania postów (minuty)",
            minimum=85, maximum=480, step=5, value=[90, 150],
            info="Agent będzie losował czas z tego przedziału. Limit Free Tier to ~1 post/85 min."
        )
        mention_interval_slider = gr.Slider(
            label="Interwał sprawdzania wzmianek (minuty)",
            minimum=15, maximum=60, step=1, value=15,
            info="Limit Free Tier to 1 zapytanie/15 minut. Nie ustawiaj niższej wartości!"
        )

    with gr.Accordion("Ustawienia 'Trybu Fana'", open=False):
        gr.Markdown("Skonfiguruj, kogo i jak często agent ma obserwować.")
        targets_textbox = gr.Textbox(
            label="Obserwowani użytkownicy (jeden na linię)",
            value=load_targets_from_file(),
            lines=5,
            info="Zapisz zmiany przyciskiem poniżej lub uruchamiając agenta."
        )
        save_targets_button = gr.Button("Zapisz listę celów")
        fan_interval_slider = gr.Slider(
            label="Interwał aktywności fana (godziny)",
            minimum=1, maximum=24, step=1, value=4
        )

    with gr.Accordion("Sterowanie Ręczne", open=True):
        gr.Markdown("Wymuś natychmiastowe wykonanie pojedynczej akcji. Uwaga na limity API!")
        
        gr.Markdown("### Główny Cykl")
        force_random_action_button = gr.Button("🚀 Wymuś Losową Akcję (jak w cyklu)", variant="primary")
        
        gr.Markdown("### Akcje Specyficzne")
        with gr.Row():
            force_post_button = gr.Button("Wymuś Post Spontaniczny")
            force_news_button = gr.Button("Wymuś Post o Newsie")
        
        gr.Markdown("### Interakcje")
        with gr.Row():
            force_mention_button = gr.Button("Wymuś Sprawdzenie Wzmianek")
            force_fan_button = gr.Button("Wymuś Akcję Fana")

    log_output = gr.Textbox(label="Logi i Wyniki Akcji", lines=10, interactive=False, autoscroll=True)

    start_button.click(
        fn=start_agent,
        inputs=[post_interval_slider, mention_interval_slider, fan_interval_slider, targets_textbox],
        outputs=[log_output]
    )
    stop_button.click(fn=stop_agent, outputs=[log_output])
    
    save_targets_button.click(fn=save_targets_to_file, inputs=[targets_textbox], outputs=[log_output])

    force_random_action_button.click(fn=force_random_action_wrapper, outputs=[log_output])

    force_post_button.click(fn=force_post_wrapper, outputs=[log_output])
    force_news_button.click(fn=force_news_post_wrapper, outputs=[log_output])
    
    force_mention_button.click(fn=force_mention_wrapper, outputs=[log_output])
    force_fan_button.click(fn=force_fan_wrapper, inputs=[targets_textbox], outputs=[log_output])
if __name__ == "__main__":
    ui.launch()