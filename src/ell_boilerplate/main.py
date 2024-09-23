# src/ell_boilerplate/main.py
import ell
from ell_boilerplate.config import EllClient
from typing import List

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
    """You are an expert novelist that writes in the style of Hemmingway. You write in lowercase."""
    ideas = generate_story_ideas(about, api_params=(dict(n=4)))

    drafts = [write_a_draft_of_a_story(idea) for idea in ideas]

    best_draft = choose_the_best_draft(drafts)


    return f"Make a final revision of this story in your voice: {best_draft}."

def main():
    EllClient.get_instance().initialize()

    # Gebruik ell functies
    story = write_a_really_good_story("a dog")
    print(story)

if __name__ == "__main__":
    main()