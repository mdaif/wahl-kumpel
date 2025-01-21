from pydantic import BaseModel


class SuggestedQuestionResponse(BaseModel):
    body: list[str]
