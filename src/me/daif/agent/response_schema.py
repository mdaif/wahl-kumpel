from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class MostImportantTopics(BaseModel):
    class FlipCard(BaseModel):
        front_text: str = Field(alias="frontText", description="The item name")
        back_text: str = Field(alias="backText", description="The item description")

    topics: list[FlipCard] = Field(description="A list of topics")


class StructuredComparisonAnswer(BaseModel):
    class Party(BaseModel):
        name: str = Field(description="The party's name")
        details: str = Field(
            description="The details of the item's stance on an a certain topic."
        )

    comparison: list[Party] = Field(
        description="A list of the parties and their stance on a certain topic."
    )


class FreeTextAnswer(BaseModel):
    free_text_answer: str = Field(
        alias="freeTextAnswer", description="Free text answer"
    )


most_important_topics_parser = PydanticOutputParser(pydantic_object=MostImportantTopics)
structured_comparison_parser = PydanticOutputParser(
    pydantic_object=StructuredComparisonAnswer
)
free_text_answer_parser = PydanticOutputParser(pydantic_object=FreeTextAnswer)
