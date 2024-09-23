# src/ell_boilerplate/main.py
import ell
from ell_boilerplate.config import EllClient

@ell.simple(model="claude-3-haiku-20240307", max_tokens=1024)
def hello(name: str):
    """You are a helpful assistant."""  # System prompt
    return f"Say hello to {name}!"  # User prompt

def main():
    EllClient.get_instance().initialize()

    # Gebruik ell functies
    greeting = hello("Sam Altman")
    print(greeting)

if __name__ == "__main__":
    main()