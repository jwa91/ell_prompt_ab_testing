Ik heb het volgende script:

```python
import ell
from pydantic import BaseModel, Field
from typing import List
from ell_boilerplate.utils.feeds import feeds_with_target_audience

def generate_feed_url(feed_name: str) -> str:
    base_url = "https://feeds.nos.nl/"
    return f"{base_url}{feed_name}"


ell.init(store='./logdir', autocommit=True, verbose=True)

class NewsSource(BaseModel):
    name: str = Field(description="Naam van de nieuwsbron")
    weight: int = Field(description="Weging op een schaal van 1 tot 10 voor deze nieuwsbron")
    reason: str = Field(description="Reden waarom deze bron wordt aanbevolen")

class PersonalizedNewsfeed(BaseModel):
    sources: List[NewsSource] = Field(description="De geselecteerde nieuwsbronnen met hun weging en reden")

@ell.complex(model="gpt-4o-2024-08-06", response_format=PersonalizedNewsfeed)
def generate_personalized_newsletter(description: str) -> PersonalizedNewsfeed:
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

# Voorbeeld aanroep
message = generate_personalized_newsletter("Ik ben een fervente volger van geopolitieke ontwikkelingen, serieuze analyses en diepgaande reportages. Daarnaast houd ik ook van af en toe wat luchtig nieuws.")
newsletter = message.parsed

# Toegang tot de individuele velden
for source in newsletter.sources:
    print(f"Naam: {source.name}, Weging: {source.weight}, Reden: {source.reason}")
```

Als ik het uitvoer, is dit de output:

```
Naam: nosnieuwsbuitenland, Weging: 3, Reden: Deze bron is perfect voor iemand met een sterke interesse in geopolitieke ontwikkelingen en internationale verhoudingen, wat aansluit bij de behoeften van de ontvanger.
Naam: nieuwsuuralgemeen, Weging: 3, Reden: Deze bron biedt serieuze analyses en diepgaande reportages, wat zeer geschikt is voor een serieus ingestelde nieuwsvolger die waarde hecht aan grondige journalistiek.
Naam: nosnieuwspolitiek, Weging: 2, Reden: Gezien de interesse van de ontvanger in geopolitiek, zal nieuws over de politieke ontwikkelingen een belangrijke aanvulling zijn op hun algemene interessegebied.
Naam: nosnieuwsopmerkelijk, Weging: 2, Reden: Om tegemoet te komen aan de behoefte aan luchtig nieuws, biedt deze bron vermakelijke en opvallende nieuwsitems die de serieuzere onderwerpen in balans brengen.
```

kun je me helpen verder te werken aan het script? ik wil een 2e call naar een llm maken op basis van de description die de eerste call ook gebruikt, maar ook de naam en weging die uit de 1e llm call komen.
Het algoritme moet het volgende doen:
1:het moet de rss feed ophalen en daaruit bepaalde velden filteren (heb al een helper functie die precies de juiste velden in de juiste json structuur opslaat)
2: a het moet de title_detail.value waarde uit die json halen
b: het moet ook de eerste 150 karakters uit de summary_detail.value halen, met de lijst van 20 titles + summary beginnetjes, moet de LLM weer aangeroepen worden

Het prompt moet iets zijn in de trend van:
"gegeven de descripton van deze persoon, kies uit deze 20 nieuwsitems de (n) items uit waarvan je verwacht dat ze het best passen bij de nieuwsbehoefte.

waarbij (n) dan de weging x1,5 is, afgerond naar hele getallen.

Ik heb voor het ophaen van de feeds al wat helper functies:
src/ell_boilerplate/utils/get_rss_feeds.py

```python
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

# Voorbeeld aanroep
fetch_filtered_feed_data("nosnieuwsbuitenland", num_items=20)
```

Hierbij ziet de output er zo uit:

```json
[
  {
    "title_detail": {
      "type": "text/plain",
      "language": null,
      "base": "https://feeds.nos.nl/nosnieuwsbuitenland",
      "value": "Vernietiging Armeens erfgoed in Nagorno-Karabach: 'Doelbewust uitwissen geschiedenis'"
    },
    "links": [
      {
        "rel": "alternate",
        "type": "text/html",
        "href": "https://nos.nl/l/2538846"
      },
      {
        "rel": "enclosure",
        "type": "image/jpeg",
        "href": "https://cdn.nos.nl/image/2024/09/28/1141058/1008x567.jpg"
      }
    ],
    "summary_detail": {
      "type": "text/html",
      "language": null,
      "base": "https://feeds.nos.nl/nosnieuwsbuitenland",
      "value": "<p>knip ivm de lengte</p>"
    },
    "published_parsed": [2024, 9, 28, 17, 9, 2, 5, 272, 0],
    "id": "https://nos.nl/l/2538846"
  }
]
```

Projectstructuur:
/Users/jw/developer/ell_boilerplate/src/ell_boilerplate/main.py - Hier komt de belangrijkste logica met de calls naar de LLM
/Users/jw/developer/ell_boilerplate/src/ell_boilerplate/utils/feeds.py - Variabele met de feedomschrijvingen
/Users/jw/developer/ell_boilerplate/src/ell_boilerplate/utils/get_rss_feeds.py - utility functies om de rss feeds aan te roepen

Graag antwoorden door de hele main.py, utils.get_rss_feeds.py en eventuele aanvullende benodigde bestandjes terug te geven, geen placeholders aub
