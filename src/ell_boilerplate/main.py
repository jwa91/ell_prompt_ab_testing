# src/ell_boilerplate/main.py
import ell

from ell_boilerplate.config import initialize_ell

def main():
    # Initialiseer ell met de juiste configuratie
    initialize_ell()

    @ell.simple(model="claude-3-haiku-20240307", max_tokens=1024)
    def hello(name: str):
        """You are a helpful assistant."""  # System prompt
        return f"Say hello to {name}!"  # User prompt

    greeting = hello("Sam Altman")
    print(greeting)

if __name__ == "__main__":
    main()
