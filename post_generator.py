# post_generator.py
import ollama
import json
import random

MODEL = 'llama3.1:latest'


class PostGenerator:
    def __init__(self, topics_file='topics.json'):
        self.topics = self._load_topics(topics_file)
        # Ten system prompt jest KLUCZOWY. Definiuje osobowość i styl AI.
        self.system_prompt = """
        You are Andrzej, a crude 30 year old man. You are having a conversation with the user and respond using short dialog responses only.
        """

    def _load_topics(self, topics_file):
        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Domyślna lista, jeśli plik nie istnieje lub jest uszkodzony
            return ["cats", "the concept of time", "pizza toppings", "aliens", "late-stage capitalism"]

    def get_random_topic(self):
        return random.choice(self.topics)

    # def generate(self, topic: str) -> str:
    #     """FAŁSZYWA funkcja do testowania. NIE łączy się z Ollama."""
    #     print(f"🤖 TEST: Udaję, że generuję post o: {topic}")
    #     #time.sleep(2)  # Udajemy, że "myślenie" zajmuje 2 sekundy
    #     return f"to jest testowy post o '{topic}'. jeśli to widzisz, aplikacja webowa działa poprawnie. 👽"

    def generate(self, topic: str) -> str:
        """Generates a shitpost based on a given topic."""
        print(f"🤖 Generating shitpost about: {topic}")

        user_prompt = f"Create a shitpost about: {topic}"

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
            return "my brain broke 👽"


# Przykład użycia (możesz to uruchomić do testów)
if __name__ == '__main__':
    generator = PostGenerator()

    # Wygeneruj post na podany temat
    post1 = generator.generate("philosophy")
    print(f"Generated Post 1: {post1}\n")

    # Wygeneruj post na losowy temat
    random_topic = generator.get_random_topic()
    post2 = generator.generate(random_topic)
    print(f"Generated Post 2: {post2}\n")