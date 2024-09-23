# src/ell_boilerplate/main.py
from dotenv import load_dotenv
import os
import ell
import openai
import anthropic
from typing import List

def initialize_ell():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY niet ingesteld")
    if not anthropic_api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY niet ingesteld")

    openai_client = openai.Client(api_key=openai_api_key)
    anthropic_client = anthropic.Client(api_key=anthropic_api_key)

    ell.init(verbose=True, store="./logdir", autocommit=True)
    ell.config.register_model("gpt-4o", openai_client)
    ell.config.register_model("gpt-4-turbo", openai_client)
    ell.config.register_model("gpt-4o-mini", openai_client)
    ell.config.register_model("claude-3-haiku-20240307", anthropic_client)
    ell.config.register_model("claude-3-5-sonnet-20240620", anthropic_client)

    print("ell is succesvol geconfigureerd met OpenAI en Anthropic clients.")

initialize_ell()

@ell.simple(model="gpt-4o-mini", temperature=1.0)
def generate_story_ideas(about : str):
    """You are an expert story ideator. Only answer in a single sentence."""
    return f"Generate a story idea about {about}."

@ell.simple(model="gpt-4o-mini", temperature=1.0)
def write_a_draft_of_a_story(idea : str):
    """You are an adept story writer. The story should only be 3 paragraphs."""
    return f"Write a story about {idea}."

@ell.simple(model="gpt-4o", temperature=0.1)
def choose_the_best_draft(drafts : List[str]):
    """You are an expert fiction editor."""
    return f"Choose the best draft from the following list: {'\n'.join(drafts)}."

@ell.simple(model="gpt-4-turbo", temperature=0.2)
def write_a_really_good_story(about : str):
    """You are an expert novelist that writes in the style of Shakespeare. You write in lowercase."""
    ideas = generate_story_ideas(about, api_params=(dict(n=4)))
    drafts = [write_a_draft_of_a_story(idea) for idea in ideas]
    best_draft = choose_the_best_draft(drafts)
    return f"Make a final revision of this story in your voice: {best_draft}."

def main():
    story = write_a_really_good_story("a dog")
    print(story)

if __name__ == "__main__":
    main()