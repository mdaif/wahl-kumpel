from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class SuggestedQuestionResponse(BaseModel):
    body: list[str]


class MostImportantTopics(BaseModel):
    topics: list[str] = Field(description="Most important topics among the parties")


most_important_topics_parser = PydanticOutputParser(pydantic_object=MostImportantTopics)
