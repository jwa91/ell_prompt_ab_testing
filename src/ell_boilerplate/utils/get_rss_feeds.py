import feedparser
import json
from typing import List
from ell_boilerplate.models.functionstructures import RSSItem, RSSLink, TitleDetail, SummaryDetail
from pydantic import ValidationError

def generate_feed_url(feed_name: str) -> str:
    """
    Genereert de volledige URL voor een gegeven feednaam.

    Args:
    - feed_name: De naam van de feed (bijv. 'nosnieuwsalgemeen').

    Returns:
    - De volledige URL van de feed.
    """
    base_url = "https://feeds.nos.nl/"
    return f"{base_url}{feed_name}"

def fetch_filtered_feed_data(feed_name: str, num_items: int = 20) -> None:
    """
    Haalt alleen de geselecteerde velden op van een RSS-feed en slaat deze op als een JSON-bestand.
    Stopt de uitvoering als verplichte velden ontbreken.

    Args:
    - feed_name: De naam van de feed (bijv. 'nosnieuwsalgemeen').
    - num_items: Het aantal items dat moet worden opgehaald (standaard en max 20).
    """
    url = generate_feed_url(feed_name)
    feed = feedparser.parse(url)

    feed_data = []
    for entry in feed.entries[:num_items]:
        try:
            item = RSSItem(
                title_detail=TitleDetail(**entry.get("title_detail")),
                links=[RSSLink(**link) for link in entry.get("links", [])],
                summary_detail=SummaryDetail(**entry.get("summary_detail")),
                published_parsed=entry["published_parsed"],
                id=entry["id"]
            )
            feed_data.append(item.model_dump())
        except KeyError as e:
            print(f"Fout: Verplicht veld ontbreekt in RSS-item: {e}")
            return
        except ValidationError as e:
            print(f"Validatiefout in RSS-item: {e}")
            return

    output_file = f"{feed_name}_filtered.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(feed_data, file, ensure_ascii=False, indent=4)

    print(f"Geselecteerde velden opgeslagen in {output_file}")