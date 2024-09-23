# src/ell_boilerplate/config.py
from dotenv import load_dotenv
import os
import ell
import openai
import anthropic

class EllClient:
    _instance = None

    def __init__(self):
        self.initialized = False

    def initialize(self):
        if self.initialized:
            return

        self._load_environment()
        self._setup_clients()
        ell.init(verbose=True)
        self.initialized = True
        print("ell is succesvol geconfigureerd met OpenAI en Anthropic clients.")

    def _load_environment(self):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.openai_api_key:
            raise EnvironmentError("OPENAI_API_KEY niet ingesteld")
        if not self.anthropic_api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY niet ingesteld")

    def _setup_clients(self):
        openai_client = openai.Client(api_key=self.openai_api_key)
        ell.config.register_model("gpt-4o", openai_client)
        anthropic_client = anthropic.Client(api_key=self.anthropic_api_key)
        ell.config.register_model("claude-3-haiku-20240307", anthropic_client)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance