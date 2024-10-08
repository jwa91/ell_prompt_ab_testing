import ell
import feedparser
from typing import List, Tuple
import sqlite3
from datetime import datetime
import uuid
import voyageai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel, Field

class SummaryEvaluation(BaseModel):
    completeness: float = Field(description="Evaluation of summary completeness, from 0 to 1")
    objectivity: float = Field(description="Evaluation of summary objectivity, from 0 to 1")

# Register adapters and converters for SQLite
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.fromisoformat(val.decode("utf-8")))

ell.init(store='./logdir', autocommit=True)

RSS_FEED_URL = "https://feeds.nos.nl/nosvoetbal"

# Initialize Voyage AI client
vo = voyageai.Client() 

def fetch_news(n: int) -> List[Tuple[str, str]]:
    """Fetch n news articles from the RSS feed."""
    feed = feedparser.parse(RSS_FEED_URL)
    return [(entry.title, entry.summary) for entry in feed.entries[:n]]

@ell.simple(model="gpt-4-turbo", temperature=0.1)
def summarize_news_v1(title: str, content: str) -> str:
    """Summarize the given news article with a focus on factual reporting."""
    return f"""You are an expert news editor known for your ability to distill complex news stories into clear, concise summaries. Your task is to summarize the following news article in 2-3 sentences, focusing on the most crucial facts and key points. Maintain a neutral, objective tone and ensure all information is accurate.

Title: {title}
Content: {content}

Summary (2-3 sentences):"""

@ell.simple(model="gpt-4o-mini", temperature=0.9)
def summarize_news_v2(title: str, content: str) -> str:
    """Summarize the given news article make it funny."""
    return f"""You are a gossip news editor known for your ability to entertain. Your task is to summarize the following news article in 2-3 sentences, focusing on the most fun points. Maintain a sensational and engaging tone

Title: {title}
Content: {content}

Summary (2-3 sentences):"""

def evaluate_summary(original: str, summary: str) -> float:
    """Evaluate the summary using vector embeddings and cosine similarity."""
    # Get embeddings for original article and summary
    original_embedding = vo.embed([original], model="voyage-3", input_type="document").embeddings[0]
    summary_embedding = vo.embed([summary], model="voyage-3", input_type="document").embeddings[0]
    
    # Calculate cosine similarity
    similarity = cosine_similarity([original_embedding], [summary_embedding])[0][0]
    
    return similarity

def save_evaluation(invocation_id: str, metric_name: str, metric_value: float):
    """Save the evaluation result to the database."""
    store = ell.get_store()
    conn_string = store.engine.url.database
    conn = sqlite3.connect(conn_string, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO evaluation (id, invocation_id, metric_name, metric_value, created_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), invocation_id, metric_name, metric_value, datetime.now()))

    conn.commit()
    conn.close()

def get_invocation_id(summary):
    """Extract the invocation_id from the __origin_trace__ frozenset."""
    for item in summary.__origin_trace__:
        if item.startswith('invocation-'):
            return item
    return None 

@ell.complex(model="gpt-4o-2024-08-06", response_format=SummaryEvaluation)
def evaluate_summary_llm(original: str, summary: str) -> SummaryEvaluation:
    """Evaluate the given summary based on completeness and objectivity."""
    return f"""You are an expert in evaluating news summaries. Your task is to assess the following summary based on two criteria: completeness and objectivity.

Completeness measures how well the summary captures all the key points of the original text. A score of 1 means the summary includes all important information, while 0 means it misses crucial points.

Objectivity measures how neutral and unbiased the summary is compared to the original text. A score of 1 means the summary maintains the same level of objectivity as the original, while 0 means it introduces significant bias or opinion.

Please evaluate the summary and provide scores for both criteria as floats between 0 and 1.

Original text:
{original}

Summary:
{summary}

Evaluation:"""

def main():
    news_articles = fetch_news(4)
    
    for i, (title, content) in enumerate(news_articles, 1):
        print(f"\nProcessing Article {i}:")
        
        original_text = f"{title}\n{content}"
        
        # Summarize with v1
        summary1 = summarize_news_v1(title, content)
        invocation_id1 = get_invocation_id(summary1)
        if invocation_id1:
            evaluation1 = evaluate_summary(original_text, summary1)
            save_evaluation(invocation_id1, "cosine_similarity", evaluation1)
            
            llm_eval1 = evaluate_summary_llm(original_text, summary1)
            
            # Extract the parsed evaluation
            parsed_eval1 = llm_eval1.content[0].parsed
            
            save_evaluation(invocation_id1, "completeness", parsed_eval1.completeness)
            save_evaluation(invocation_id1, "objectivity", parsed_eval1.objectivity)
        else:
            print(f"Warning: Could not find invocation_id for summary1 of article {i}")
            evaluation1 = None
            parsed_eval1 = None

        # Summarize with v2
        summary2 = summarize_news_v2(title, content)
        invocation_id2 = get_invocation_id(summary2)
        if invocation_id2:
            evaluation2 = evaluate_summary(original_text, summary2)
            save_evaluation(invocation_id2, "cosine_similarity", evaluation2)

            llm_eval2 = evaluate_summary_llm(original_text, summary2)
            
            # Extract the parsed evaluation
            parsed_eval2 = llm_eval2.content[0].parsed
            
            save_evaluation(invocation_id2, "completeness", parsed_eval2.completeness)
            save_evaluation(invocation_id2, "objectivity", parsed_eval2.objectivity)
        else:
            print(f"Warning: Could not find invocation_id for summary2 of article {i}")
            evaluation2 = None
            parsed_eval2 = None

        print(f"Artikel {i}:")
        print(f"Titel: {title}")
        print(f"Samenvatting 1: {summary1}")
        print(f"Evaluatie 1 (Cosine Similarity): {evaluation1}")
        print(f"Evaluatie 1 (Completeness): {parsed_eval1.completeness if parsed_eval1 else 'N/A'}")
        print(f"Evaluatie 1 (Objectivity): {parsed_eval1.objectivity if parsed_eval1 else 'N/A'}")
        print(f"Invocation ID 1: {invocation_id1}")
        print(f"Samenvatting 2: {summary2}")
        print(f"Evaluatie 2 (Cosine Similarity): {evaluation2}")
        print(f"Evaluatie 2 (Completeness): {parsed_eval2.completeness if parsed_eval2 else 'N/A'}")
        print(f"Evaluatie 2 (Objectivity): {parsed_eval2.objectivity if parsed_eval2 else 'N/A'}")
        print(f"Invocation ID 2: {invocation_id2}\n")


if __name__ == "__main__":
    main()