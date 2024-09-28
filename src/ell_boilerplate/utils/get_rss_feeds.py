import feedparser
import json
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

class RSSLink(BaseModel):
    rel: Optional[str] = Field(None, description="Het type relatie van de link (bijv. 'alternate')")
    type: Optional[str] = Field(None, description="Het type inhoud waar de link naar verwijst (bijv. 'text/html')")
    href: Optional[str] = Field(None, description="De URL van de link")

class TitleDetail(BaseModel):
    type: Optional[str] = Field(None, description="Het type van de titel (bijv. 'text/plain')")
    language: Optional[str] = Field(None, description="De taal van de titel")
    base: Optional[str] = Field(None, description="De basis-URL van de titel")
    value: str = Field(..., description="De feitelijke waarde van de titel") 

class SummaryDetail(BaseModel):
    type: Optional[str] = Field(None, description="Het type van de samenvatting (bijv. 'text/html')")
    language: Optional[str] = Field(None, description="De taal van de samenvatting")
    base: Optional[str] = Field(None, description="De basis-URL van de samenvatting")
    value: str = Field(..., description="De feitelijke waarde van de samenvatting")  

class RSSItem(BaseModel):
    title_detail: TitleDetail = Field(..., description="Details over de titel van het nieuwsitem")  
    links: Optional[List[RSSLink]] = Field(None, description="Een lijst van links gerelateerd aan het item")
    summary_detail: SummaryDetail = Field(..., description="Details over de samenvatting")  
    published_parsed: tuple = Field(..., description="De publicatiedatum als gestructureerde tijd")  
    id: str = Field(..., description="Een unieke identifier voor het item")  

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
