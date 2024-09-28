import ell
import json
from typing import List
from ell_boilerplate.utils.feeds import feeds_with_target_audience
from ell_boilerplate.utils.get_rss_feeds import fetch_filtered_feed_data
from ell_boilerplate.models.functionstructures import RSSItem
from ell_boilerplate.models.llm_response_structure import (
    NewsSource, 
    PersonalizedNewsfeed, 
    SelectedNewsItem, 
    SelectedNewsItems,
    FinalNewsItem,
    FinalNewsItems
)

ell.init(store='./logdir', autocommit=True, verbose=True)

@ell.complex(model="gpt-4o-2024-08-06", response_format=PersonalizedNewsfeed)
def generate_personalized_newsfeed(description: str) -> PersonalizedNewsfeed:
    """
    Je bent een persoonlijke nieuwsbrief redacteur. Op basis van een persoonlijke omschrijving geef je tussen de 2 en 3
    nieuwsbronnen terug, elk met een weging op een schaal van 1 tot 10 die samen altijd optellen tot exact 10. Geef ook kort de reden voor het opnemen van elke bron.
    Kies altijd uit de meegegeven nieuwsbronnen.
    """
    available_feeds = ", ".join([f"{feed['name']} (Doelgroep: {feed['audience']})" for feed in feeds_with_target_audience])
    return f"""
    Gebaseerd op de volgende omschrijving van de ontvanger: "{description}", kies je minimaal 2 en maximaal 3 nieuwsbronnen
    die het beste passen bij hun nieuwsbehoefte. Geef aan waarom je deze bronnen kiest en wijs elke bron een weging toe
    in procenten. De totale weging moet precies 10 zijn. Beschikbare nieuwsbronnen: {available_feeds}
    """

@ell.complex(model="gpt-4o-2024-08-06", response_format=SelectedNewsItems)
def select_news_items(description: str, articles: List[RSSItem], source: NewsSource) -> SelectedNewsItems:
    """
    Je bent een redacteur die artikelen selecteert voor een nieuwsbrief. Op basis van de beschrijving van de ontvanger
    en de aangeleverde artikelen, selecteer je de beste artikelen die aansluiten bij de nieuwsbehoefte.
    """
    num_items = round(source.weight * 1.5)
    titles_with_summaries = "\n".join([f"ID: {article.id}, Title: {article.title_detail.value}, Summary: {article.summary_detail.value[:100]}" for article in articles])
    return f"""
    beschrijving van de ontvanger: "{description}"
    kies de {num_items} items die het best passen bij de nieuwsbehoefte
    Geef een argument waarom het belangrijk is om dit nieuwsbericht op te nemen in de nieuwsbrief

    {titles_with_summaries}

    Geef je antwoord in de vorm van een lijst van SelectedNewsItem objecten, elk met een ID, Titel en reden.
    """

@ell.complex(model="gpt-4o-2024-08-06", response_format=FinalNewsItems)
def create_final_newsletter(description: str, selected_items: List[SelectedNewsItem]) -> FinalNewsItems:
    """
    Je bent hoofdredacteur van een persoonlijke nieuwsbrief. Je redacteuren hebben een lijst opgesteld met alle mogelijke
    onderwerpen die vandaag behandeld kunnen worden. Maak de uiteindelijke selectie van 5 nieuwsitems.
    """
    items_str = "\n".join([f"ID: {item.id}, Title: {item.title}, Reason: {item.reason}" for item in selected_items])
    return f"""
    Je bent hoofdredacteur van een persoonlijke nieuwsbrief. Je redacteuren hebben een lijst opgesteld met alle mogelijke
    onderwerpen die vandaag behandeld kunnen worden. Maak de uiteindelijke selectie van 5 nieuwsitems. Hou rekening met
    de nieuwsbehoefte van de lezer: "{description}"

    Maar zorg er bij je selectie ook voor dat je er een goede coherente nieuwsbrief van kunt maken. Kijk of er
    overkoepelende verhaallijnen zijn of thema's die je aan kunt stippen. Maak een logische indeling en maak vervolgens
    voor elk nieuwsitem dat in je uiteindelijke selectie zit een korte instructie hoe dit nieuwsitem benaderd moet worden. hou er rekening mee dat deze benadering geschikt is voor een stukje tekst dat dient als 1 van de 5 stukjes tekst voor een nieuwsbrief. Dus niet te lang, geen diepgaande analyses.

    Hier zijn de beschikbare nieuwsitems:

    {items_str}

    Geef je antwoord in de vorm van een lijst van 5 FinalNewsItem objecten, elk met een ID, Titel, positie (1-5), en benadering.
    """

@ell.simple(model="gpt-4o-mini", temperature=1.0)
def generate_news_item_versions(news_item: FinalNewsItem):
    """
    Je bent een getalenteerde nieuws schrijver. Schrijf een item voor een nieuwsbrief. 
    """
    return f"""
    Schrijf een nieuwsitem met de volgende details:
    Titel: {news_item.title}
    Benadering: {news_item.approach}
    """

@ell.simple(model="gpt-4o", temperature=0.1)
def choose_and_improve_best_version(versions: List[str], news_item: FinalNewsItem):
    """
    Je bent een ervaren redacteur. Kies de beste versie van het nieuwsartikel en verbeter het waar nodig.
    """
    versions_str = "\n\n".join([f"Versie {i+1}:\n{version}" for i, version in enumerate(versions)])
    return f"""
    Kies de beste versie van het volgende nieuwsartikel en verbeter het waar nodig:
    {versions_str}
    """

@ell.simple(model="gpt-4-turbo", temperature=0.2)
def compile_final_newsletter(final_versions: List[str], description: str):
    """
    Je bent hoofdredacteur van een nieuwsbrief. Maak op basis van de volgende nieuwsartikelen een coherente nieuwsbrief.
    Voeg waar nodig overgangen of verbindende teksten toe.
    """
    articles_str = "\n\n".join(final_versions)
    return f"""
    Je bent hoofdredacteur van een nieuwsbrief. Maak op basis van de volgende nieuwsartikelen een coherente nieuwsbrief.
    Voeg waar nodig overgangen of verbindende teksten toe.
    Beschrijving van de lezer: "{description}"

    Nieuwsartikelen:
    {articles_str}

    Geef het eindresultaat in markdown formaat.
    """

def generate_newsletter(description: str) -> str:
    # Stap 1: Genereer een gepersonaliseerde nieuwsfeed
    personalized_news_message = generate_personalized_newsfeed(description)
    personalized_news = personalized_news_message.parsed

    all_selected_news_items = []
    for source in personalized_news.sources:
        fetch_filtered_feed_data(source.name)
        json_filename = f"{source.name}_filtered.json"

        with open(json_filename, "r", encoding="utf-8") as file:
            articles = [RSSItem(**item) for item in json.load(file)]

        selected_news_items_message = select_news_items(description, articles, source)
        selected_news_items = selected_news_items_message.parsed
        all_selected_news_items.extend(selected_news_items.items)

    final_newsletter_message = create_final_newsletter(description, all_selected_news_items)
    final_news_items = final_newsletter_message.parsed.items

    # Nu, voor elk van de finale nieuwsitems, genereer 2 versies en kies de beste
    final_versions = []
    for news_item in final_news_items:
        # Genereer 2 versies
        versions_messages = generate_news_item_versions(news_item, api_params={'n': 2})
        versions = [str(message) for message in versions_messages]
        print(f"Generated versions for news item {news_item.id}:")
        for i, version in enumerate(versions):
            print(f"Version {i+1}:\n{version}\n")

        # Kies en verbeter de beste versie
        best_version_message = choose_and_improve_best_version(versions, news_item)
        best_version = str(best_version_message)

        final_versions.append(best_version)

    # Compileer de uiteindelijke nieuwsbrief
    final_newsletter_message = compile_final_newsletter(final_versions, description)
    final_newsletter = str(final_newsletter_message)

    # Sla de uiteindelijke nieuwsbrief op als markdown
    with open('final_newsletter.md', 'w', encoding='utf-8') as f:
        f.write(final_newsletter)

    return final_newsletter


# Voorbeeld aanroep
result = generate_newsletter("Ik ben een fervente volger van geopolitieke ontwikkelingen, serieuze analyses en diepgaande reportages. Daarnaast houd ik ook van af en toe wat luchtig nieuws.")
