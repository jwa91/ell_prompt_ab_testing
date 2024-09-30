import ell
import feedparser
from typing import List, Tuple

ell.init(store='./logdir', autocommit=True)

RSS_FEED_URL = "https://feeds.nos.nl/nosvoetbal"

def fetch_news(n: int) -> List[Tuple[str, str]]:
    """Fetch n news articles from the RSS feed."""
    feed = feedparser.parse(RSS_FEED_URL)
    return [(entry.title, entry.summary) for entry in feed.entries[:n]]

@ell.simple(model="gpt-4-turbo", temperature=0.1)
def summarize_news(title: str, content: str) -> str:
    """Summarize the given news article with a focus on factual reporting."""
    return f"""You are an expert news editor known for your ability to distill complex news stories into clear, concise summaries. Your task is to summarize the following news article in 2-3 sentences, focusing on the most crucial facts and key points. Maintain a neutral, objective tone and ensure all information is accurate.

Title: {title}
Content: {content}

Summary (2-3 sentences):"""

def main():
    news_articles = fetch_news(2)
    
    for i, (title, content) in enumerate(news_articles, 1):
        print(f"\nProcessing Article {i}:")
        
        summary = summarize_news(title, content)

        print(f"Artikel {i}:")
        print(f"Titel: {title}")
        print(f"Samenvatting: {summary}\n")

if __name__ == "__main__":
    main()