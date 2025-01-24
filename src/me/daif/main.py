from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from me.daif.agent.kumpel import answer_question
from me.daif.agent.language import SupportedLanguage
from me.daif.agent.response_schema import (
    most_important_topics_parser,
    structured_comparison_parser,
    free_text_answer_parser,
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health():
    return {"status": "OK"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/topics")
async def most_important_topics(
    count: int = 10, language: SupportedLanguage = SupportedLanguage.english
):
    question = f"""
        What is the most important {count} common topics among all parties ?
        I want a list of items like healthcare, pension, .. etc
        For each item I want:
        1. The item name (like healthcare, pension, ...etc).
        2. description: A text that says: Make a comparison between the stances of all parties on <the item name from step 1>.
        Answer both points in the {language} language, and use friendly non-official tone.
        Provide the output in the following JSON format:
        {most_important_topics_parser.get_format_instructions()}
    """
    answer = await answer_question(question, language)
    return most_important_topics_parser.parse(answer)


@app.get("/answer-question")
async def answer_user_question(question: str):
    question = f"""
    You help Wahlkumpel, an AI assistant that helps people get informed on the political parties running for the
    upcoming elections in February 2025.
    
    Answer the question: {question}
    
    If the question is of day-to-day nature, like small talk, or greetings answer freely.
    
    If you can safely assume that the question is of political or social nature, assume it asks for comparison between
    the stances of all parties on a the topic of the question, and your answer must include information about all the
    parties.
    
    If the question does not provide enough context, feel free to say you don't know the answer, and offer assistance on
    answering election-related questions.
    
    The language you write your answer in should be the same language of the question, and use friendly non-official 
    tone.
    
    If the question is about comparing the stances of different parties, Provide the output in the following JSON format:
    {structured_comparison_parser.get_format_instructions()}
    
    Otherwise, provide the output in the following json format
    {free_text_answer_parser.get_format_instructions()}
    """
    answer = await answer_question(question, None)
    if "comparison" in answer:
        return structured_comparison_parser.parse(answer)
    else:
        return free_text_answer_parser.parse(answer)
