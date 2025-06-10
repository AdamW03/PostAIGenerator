# main.py

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# Upewnij się, że nazwa pliku i klasy są poprawne
from post_generator import PostGenerator

# Jeśli używasz twittera, odkomentuj:
import twitter_poster

app = FastAPI()
templates = Jinja2Templates(directory="templates")
generator = PostGenerator()


# Ta funkcja obsługuje PIERWSZE załadowanie strony.
# Jest bardzo szybka - losuje tylko temat i renderuje HTML.
# NIE wywołuje modelu AI.
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    random_topic = generator.get_random_topic()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "topic": random_topic,
        "post": ""  # Zwracamy pusty post na początku
    })


# Ta funkcja jest wywoływana DOPIERO, gdy użytkownik WYPEŁNI formularz
# i kliknie przycisk "Generate Shitpost".
# To TUTAJ wywołujemy model AI, co może chwilę potrwać.
@app.post("/", response_class=HTMLResponse)
async def create_post(request: Request, topic: str = Form(...)):
    # Wywołanie modelu AI - to jest ta długa operacja
    post_text = generator.generate(topic)

    # Jeśli chcesz od razu postować na Twitterze, odkomentuj poniższą linię
    twitter_poster.post_to_x(post_text)

    # Zwracamy stronę ponownie, tym razem z wygenerowanym postem
    return templates.TemplateResponse("index.html", {
        "request": request,
        "topic": topic,
        "post": post_text
    })