from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class SuggestedQuestionResponse(BaseModel):
    body: list[str]


class MostImportantTopics(BaseModel):
    class FlipCard(BaseModel):
        front_text: str = Field(alias="frontText", description="The item name")
        back_text: str = Field(alias="backText", description="The item description")

    topics: list[FlipCard] = Field(description="A list of topics")


most_important_topics_parser = PydanticOutputParser(pydantic_object=MostImportantTopics)
