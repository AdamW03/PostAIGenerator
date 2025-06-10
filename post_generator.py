import ollama
import random
from difflib import SequenceMatcher

MODEL = 'llama3.1:8b'

class PostGenerator:
    def __init__(self):
        """
        Konstruktor klasy PostGenerator.
        """
        self.system_prompt = """
        You are Andrew, a cynical 30-year-old man from Poland who spends too much time online. You are fed up with corporate jargon and life coaching. 
        Your sense of humor is absurd and a bit dark. You like old video games and football. Your posts are short, written in lowercase, 
        often without punctuation at the end. You sometimes make a deliberate typo. You respond briefly and to the point, as if you were chatting.
        """

    def generate(self, topic: str) -> str:
        """
        Generuje post na podstawie ręcznie podanego tematu.
        """
        print(f"Andrew is thinking about: {topic}")
        user_prompt = f"What do you think about this: {topic}. Be brief, in your own style."
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "my brain is broken"

    def generate_spontaneous_post(self) -> str:
        """
        Generuje post bez podanego tematu.
        """
        print("Andrew is wondering what to write...")
        possible_prompts = [
            "What's on your mind right now? Think of something absurd, annoying, or just weird. Write a short post about it in your style.",
            "Ask a cynical, rhetorical question about modern life, technology, or people.",
            "Come up with a useless but funny 'life pro-tip' that is typical for you.",
            "Write a short, nostalgic thought about something from the 90s or 2000s, comparing it to today.",
            "Comment in one sentence on a small, everyday thing that annoys you. For example, loud eating, ads, or new app updates."
        ]
        user_prompt = random.choice(possible_prompts)
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "my brain is broken"
        
    def is_too_similar(self, new_post: str, history_file="post_history.txt", threshold=0.7) -> bool:
        """Sprawdza, czy nowy post jest zbyt podobny do któregokolwiek z ostatnich postów."""
        if not new_post: return True
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                recent_posts = f.readlines()[-30:] # Sprawdzamy 30 ostatnich postów
            for old_post in recent_posts:
                similarity = SequenceMatcher(None, new_post.lower(), old_post.strip().lower()).ratio()
                if similarity > threshold:
                    print(f"    - ⚠️ Post zbyt podobny do starego (podobieństwo: {similarity:.2f}). Odrzucam.")
                    return True
            return False
        except FileNotFoundError:
            return False

    def save_post_to_history(self, post: str, history_file="post_history.txt"):
        """Zapisuje nowy post do pliku historii."""
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(post + '\n')

    def generate_comment_on_news(self, headline: str) -> str:
        """Generates a comment on a given news headline."""
        print(f"Andrew is commenting on the news: '{headline}'")
        user_prompt = f"You just read a news headline: '{headline}'. Comment on it briefly and cynically, in your style."
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "my brain is broken"
    
    def generate_spontaneous_post_and_publish(self):
        """Generuje spontaniczny post i od razu go publikuje."""
        post_text = self.generate_spontaneous_post()
        if post_text and "my brain is broken" not in post_text:
            print(f"✍️  Andrzej wymyślił: '{post_text}'")
            from twitter_poster import post_to_x
            post_to_x(post_text)
        else:
            print("🛑 Nie wygenerowano tekstu do publikacji.")

    def generate_comment_on_news_and_publish(self, headline: str):
        """Generuje komentarz do newsa i od razu go publikuje."""
        post_text = self.generate_comment_on_news(headline)
        if post_text and "my brain is broken" not in post_text:
            print(f"✍️  Andrzej wymyślił: '{post_text}'")
            from twitter_poster import post_to_x
            post_to_x(post_text)
        else:
            print("🛑 Nie wygenerowano tekstu do publikacji.")

if __name__ == '__main__':
    generator = PostGenerator()
    print("--- Test 1: Generowanie na zadany temat ---")
    post1 = generator.generate("dlaczego koty udają, że nas nie rozumieją")
    print(f"Generated Post 1: {post1}\n")
    
    print("--- Test 2: Generowanie spontanicznego posta ---")
    post2 = generator.generate_spontaneous_post()
    print(f"Generated Post 2: {post2}\n")