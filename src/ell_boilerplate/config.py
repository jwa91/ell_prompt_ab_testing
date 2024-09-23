# src/ell_boilerplate/config.py
from dotenv import load_dotenv
import os
import ell
import openai
import anthropic

_ell_initialized = False

def initialize_ell():
    global _ell_initialized

    if _ell_initialized:
        return
    
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"):
        load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY niet ingesteld")
    if not anthropic_api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY niet ingesteld")

    # Stel de clients in
    openai_client = openai.Client(api_key=openai_api_key)
    ell.config.register_model("gpt-4o", openai_client)
    anthropic_client = anthropic.Client(api_key=anthropic_api_key)
    ell.config.register_model("claude-3-haiku-20240307", anthropic_client)

    # Initialiseer ell met verbose mode
    ell.init(verbose=True)
    _ell_initialized = True
    print("ell is succesvol geconfigureerd met OpenAI en Anthropic clients.")
