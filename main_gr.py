# main_gr.py (wersja z Gradio)
import gradio as gr
from post_generator import PostGenerator

generator = PostGenerator()

def generate_interface(topic):
    if not topic:
        topic = generator.get_random_topic()
    return generator.generate(topic)

iface = gr.Interface(
    fn=generate_interface,
    inputs=gr.Textbox(lines=1, placeholder="Enter topic or leave blank for random..."),
    outputs="text",
    title="AI Shitpost Factory 👽",
    description="Generate chaotic, low-effort posts for your social media needs. Powered by Ollama.",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()