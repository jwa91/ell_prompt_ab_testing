import ell
import json
from pydantic import BaseModel, Field
from typing import List
from ell_boilerplate.utils.feeds import feeds_with_target_audience
from ell_boilerplate.utils.get_rss_feeds import fetch_filtered_feed_data, RSSItem

ell.init(store='./logdir', autocommit=True, verbose=True)

class NewsSource(BaseModel):
    name: str = Field(description="Naam van de nieuwsbron")
    weight: int = Field(description="Weging op een schaal van 1 tot 10 voor deze nieuwsbron")
    reason: str = Field(description="Reden waarom deze bron wordt aanbevolen")

class PersonalizedNewsfeed(BaseModel):
    sources: List[NewsSource] = Field(description="De geselecteerde nieuwsbronnen met hun weging en reden")

class RankedNewsItem(BaseModel):
    id:str = Field(description="id van het nieuwsitem")
    title:str = Field(description="title van het nieuwsitem")
    position: int = Field(description="waarde om nieuwsitem te prioriteren. 1 is het meest aanbevolen item")
    reason: str = Field(description="Reden waarom dit item wordt aanbevolen")

class RankedNewsItems(BaseModel):
    items: List[RankedNewsItem] = Field(description="De geselecteerde nieuwsitems met hun title, positie en reden")


@ell.complex(model="gpt-4o-2024-08-06", response_format=PersonalizedNewsfeed)
def generate_personalized_newsfeed(description: str) -> PersonalizedNewsfeed:
    """
    Je bent een persoonlijke nieuwsbrief redacteur. Op basis van een persoonlijke omschrijving geef je tussen de 4 en 8
    nieuwsbronnen terug, elk met een weging op een schaal van 1 tot 10 die samen altijd optellen tot exact 10. Geef ook de reden voor het opnemen van elke bron.
    Kies altijd uit de meegegeven nieuwsbronnen.
    """
    available_feeds = ", ".join([f"{feed['name']} (Doelgroep: {feed['audience']})" for feed in feeds_with_target_audience])
    return f"""
    Gebaseerd op de volgende omschrijving van de ontvanger: "{description}", kies je minimaal 4 en maximaal 8 nieuwsbronnen
    die het beste passen bij hun nieuwsbehoefte. Geef aan waarom je deze bronnen kiest en wijs elke bron een weging toe
    in procenten. De totale weging moet precies 10 zijn. Beschikbare nieuwsbronnen en hun doelgroepen: {available_feeds}
    """

@ell.complex(model="gpt-4o-2024-08-06", response_format=RankedNewsItems)
def rank_news_items(description: str, articles: List[RSSItem], weight: int) -> RankedNewsItems:
    """
    Je bent een redacteur die artikelen rangschikt voor een nieuwsbrief. Op basis van de beschrijving van de ontvanger
    en de aangeleverde artikelen, rangschik je de beste artikelen die aansluiten bij de nieuwsbehoefte. Het aantal artikelen
    is gelijk aan de weging van de nieuwsbron vermenigvuldigd met 1,5, afgerond naar het dichtstbijzijnde hele getal.
    """
    num_items = round(weight * 1.5)
    titles_with_summaries = "\n".join([f"ID: {article.id}, Title: {article.title_detail.value}, Summary: {article.summary_detail.value[:150]}" for article in articles])
    return f"""
    Gegeven de volgende beschrijving van de ontvanger: "{description}" en de onderstaande lijst met 20 nieuwsitems, kies
    de {num_items} items waarvan je verwacht dat ze het best passen bij de nieuwsbehoefte en geef ze een positie op basis van prioriteit.
    Geef ook de reden voor elke keuze.

    {titles_with_summaries}
    """

def generate_newsletter(description: str):
    # Eerste call: genereren van gepersonaliseerde nieuwsbronnen
    personalized_news = generate_personalized_newsfeed(description).parsed
    
    all_ranked_news_items = []

    # Tweede call: ophalen van artikelen en rangschikken van items
    for source in personalized_news.sources:
        fetch_filtered_feed_data(source.name)  # JSON-bestand genereren met de artikelen van de feed
        json_filename = f"{source.name}_filtered.json"
        
        with open(json_filename, "r", encoding="utf-8") as file:
            articles = [RSSItem(**item) for item in json.load(file)]
        
        # Rangschik de artikelen op basis van de eerste call output
        ranked_news_items = rank_news_items(description, articles, source.weight).parsed
        all_ranked_news_items.extend(ranked_news_items.items)
    
    # Print de gerangschikte nieuwsitems
    for item in all_ranked_news_items:
        print(f"ID: {item.id}, Title: {item.title}, Position: {item.position}, Reason: {item.reason}")

# Voorbeeld aanroep
generate_newsletter("Ik ben een fervente volger van geopolitieke ontwikkelingen, serieuze analyses en diepgaande reportages. Daarnaast houd ik ook van af en toe wat luchtig nieuws.")