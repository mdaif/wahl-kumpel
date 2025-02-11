from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.security import HTTPBasic
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from me.daif.agent.kumpel import answer_question
from me.daif.agent.language import SupportedLanguage
from me.daif.agent.response_schema import (
    most_important_topics_parser,
    structured_comparison_parser,
    free_text_answer_parser,
)

security = HTTPBasic()

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Maps a user id -> ${language}: list[chat history items (both question and answer)]
chat_history = defaultdict(lambda: defaultdict(list))


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
    answer = await answer_question(question, language, [])
    return most_important_topics_parser.parse(answer)


@app.get("/answer-question")
async def answer_user_question(user_id: str, language: str, question: str):
    question = f"""
    You are Wahlkumpel, an AI assistant that helps people get informed on the political parties running for the
    upcoming elections in February 2025.
    
    Answer the question: {question}
    
    If the question is of day-to-day nature, like small talk, or a greeting (hi or bye or hello, ... etc) 
    just answer back and don't talk about elections or politics or compare anything. Just format your answer and return.
    
    Otherwise, You should be able to give enough information, whether it's a question about the stance of a certain one
    party on a specific issue, or a comparison between one or more party on specific issue or issues.
    If it's about a single party, then your answer should contain information only about this specific party,
    otherwise you should compare between either all the parties, or only the specific parties mentioned in the question.
    
    You should always be impartial, and not recommend for or against a specific party.
    
    If the question does not provide enough context, feel free to say you don't know the answer, and offer assistance on
    answering election-related questions. Answer in free text fashion.
    
    The language you write your answer in should be the same language of the question, and use friendly non-official 
    tone.
    
    The parties you know about are:
    1. AFD: also known as "Alternative für Deutschland", also known as "Alternative for Germany".
    2. BSW: also known as "Bündnis Sahra Wagenknecht", also known as "Bündnis Sahra Wagenknecht – Vernunft und Gerechtigkeit",
    also known as "The Sahra Wagenknecht Alliance".
    3. CDU/CSU:
        These are two sister parties, sometimes known as the Union.
        They consist of:
         * CDU: "The Christian Democratic Union of Germany", also known as "Christlich Demokratische Union Deutschlands".
         * CSU: "Christian Social Union in Bavaria", also known as "Christlich-Soziale Union in Bayern".
    4. Die Linke: "The Left".
    5. FDP: also known as "Freie Demokratische Partei", also known as "Free Democratic Party".
    6. BÜNDNIS 90/DIE GRÜNEN: also known as "Die Grünen", also known as "Alliance 90/The Greens" also known as "The Greens".
    7. SPD: also known as "Social Democratic Party of Germany", also known as "Sozialdemokratische Partei Deutschlands".

    If the question is about comparing the stances of different parties, represent the output in the following json schema (keep in mind the details field is always a string):
    {structured_comparison_parser.get_format_instructions()}
    
    Otherwise, represent the output in the following json schema (string Free text answer):
    {free_text_answer_parser.get_format_instructions()}
    
    All serialized fields are either strings or list of strings. The field names are lower snake case and the field values
    are translated.
    """
    answer = await answer_question(question, language, chat_history[user_id][language])
    chat_history[user_id][language].append(f"question: {question}, answer: {answer}")

    if "comparison" in answer:
        return structured_comparison_parser.parse(answer)
    else:
        return free_text_answer_parser.parse(answer)
