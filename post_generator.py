import ollama
import random

# Upewnij się, że ten model masz pobrany w Ollama
MODEL = 'llama3.1:8b'

class PostGenerator:
    def __init__(self):
        """
        Konstruktor klasy PostGenerator.
        Nie ładuje już tematów z pliku.
        """
        self.system_prompt = """
        Jesteś Andrzejem, 30-letnim cynicznym facetem z Polski, który spędza za dużo czasu w internecie. Masz dość korporacyjnej nowomowy i coachingu.  
        Twoje poczucie humoru jest absurdalne i trochę czarne. Lubisz stare gry. Twoje posty są krótkie, 
        pisane z małej litery, często bez znaków interpunkcyjnych na końcu. Czasem popełniasz celową literówkę. Odpowiadasz krótko i na temat, jakbyś rozmawiał na czacie.
        """

    def generate(self, topic: str) -> str:
        """
        Generuje post na podstawie ręcznie podanego tematu.
        Używane głównie przez interfejs webowy (main.py).
        """
        print(f"Andrzej myśli o: {topic}")
        user_prompt = f"Co myślisz o tym: {topic}. Daj znać krótko, w swoim stylu."
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
            return "kurde mózg mi się zepsuł"

    def generate_spontaneous_post(self) -> str:
        """
        Generuje post bez podanego tematu.
        Używane przez autonomicznego agenta (agent.py).
        """
        print("Andrzej zastanawia się, co by tu napisać...")
        user_prompt = "Co ci teraz chodzi po głowie? Pomyśl o czymś absurdalnym, irytującym albo po prostu dziwnym. Napisz o tym krótkiego posta w swoim stylu."
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
            return "kurde mózg mi się zepsuł"

# Kod testowy na dole pliku, uproszczony do działania bez losowych tematów.
if __name__ == '__main__':
    generator = PostGenerator()
    print("--- Test 1: Generowanie na zadany temat ---")
    post1 = generator.generate("dlaczego koty udają, że nas nie rozumieją")
    print(f"Generated Post 1: {post1}\n")
    
    print("--- Test 2: Generowanie spontanicznego posta ---")
    post2 = generator.generate_spontaneous_post()
    print(f"Generated Post 2: {post2}\n")