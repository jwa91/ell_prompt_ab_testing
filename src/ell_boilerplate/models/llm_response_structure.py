from pydantic import BaseModel, Field
from typing import List

class NewsSource(BaseModel):
    name: str = Field(description="Naam van de nieuwsbron")
    weight: int = Field(description="Weging op een schaal van 1 tot 10 voor deze nieuwsbron")

class PersonalizedNewsfeed(BaseModel):
    sources: List[NewsSource] = Field(description="De geselecteerde nieuwsbronnen met hun weging")

class SelectedNewsItem(BaseModel):
    id: str = Field(description="id van het nieuwsitem")
    title: str = Field(description="title van het nieuwsitem")
    reason: str = Field(description="Reden waarom dit item wordt aanbevolen")

class SelectedNewsItems(BaseModel):
    items: List[SelectedNewsItem] = Field(description="De geselecteerde nieuwsitems met hun title en reden")

class FinalNewsItem(BaseModel):
    id: str = Field(description="id van het nieuwsitem")
    title: str = Field(description="titel van het nieuwsitem")
    position: int = Field(description="positie van het nieuwsitem(1 tm 5)")
    approach: str = Field(description="korte instructie hoe het item te benaderen (opgewekt, serieus, deepdive bijv.)")

class FinalNewsItems(BaseModel):
    items: List[FinalNewsItem]