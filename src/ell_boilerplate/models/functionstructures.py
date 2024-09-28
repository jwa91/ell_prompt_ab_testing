from pydantic import BaseModel, Field
from typing import List, Optional

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