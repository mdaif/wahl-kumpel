from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from me.daif.agent.kumpel import answer_question
from me.daif.agent.language import SupportedLanguage
from me.daif.agent.response_schema import (
    SuggestedQuestionResponse,
    most_important_topics_parser,
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health():
    return {"status": "OK"}


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/suggest-predefined-questions")
async def suggest_predefined_questions(
    language: SupportedLanguage,
) -> SuggestedQuestionResponse:
    # TODO: This is temporary, we should generate some questions dynamically.
    match language:
        case SupportedLanguage.english:
            return SuggestedQuestionResponse(
                body=[
                    "For each party of the following parties: "
                    "AFD, BSW, CDU/CSU, FDP, Die Grünen, Die Linke, SPD "
                    "Tell me the stance of the party on energy. In particular the solar farms, wind farms, "
                    "coal, wood, and fossil fuels. "
                    "Make your answer concise and in a simple language.",
                    "For each party of the following parties: "
                    "AFD, BSW, CDU/CSU, FDP, Die Grünen, Die Linke, SPD "
                    "Tell me the stance of the party on illegal immigration. "
                    "Make your answer concise and in a simple language.",
                    "For each party of the following parties: "
                    "AFD, BSW, CDU/CSU, FDP, Die Grünen, Die Linke, SPD "
                    "Tell me the stance of the party on the relations with Russia. "
                    "Make your answer concise and in a simple language.",
                    "Given all the knowledge you have on the parties, what could be the top "
                    "20 questions I can ask in order to be able to make an informative "
                    "decision on whom to vote for ?",
                ]
            )
        case SupportedLanguage.german:
            return SuggestedQuestionResponse(
                body=[
                    "Für jede der folgenden Parteien"
                    "AFD, BSW, CDU/CSU, FDP, Die Grünen, Die Linke, SPD "
                    "Erklären Sie mir die Haltung der Partei zur Energiepolitik. Insbesondere zu Solarparks, "
                    "Windkraftanlagen, Kohle, Holz und fossilen Brennstoffen. "
                    "Machen Sie Ihre Antwort prägnant und in einfacher Sprache.",
                    "Für jede der folgenden Parteien:"
                    "AFD, BSW, CDU/CSU, FDP, Die Grünen, Die Linke, SPD "
                    "Erklären Sie mir die Haltung der Partei zur illegalen Einwanderung. "
                    "Machen Sie Ihre Antwort prägnant und in einfacher Sprache.",
                    "Für jede der folgenden Parteien: "
                    "AFD, BSW, CDU/CSU, FDP, Die Grünen, Die Linke, SPD "
                    "Erklären Sie mir die Haltung der Partei zu den Beziehungen zu Russland. "
                    "Machen Sie Ihre Antwort prägnant und in einfacher Sprache.",
                    "Angesichts aller Kenntnisse über die Parteien, welche wären die 20 wichtigsten Fragen, die ich "
                    "stellen könnte, um eine fundierte Entscheidung darüber zu treffen, wen ich wählen soll?",
                ]
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
        2. description: A text that says: Compare between the stances of all parties on the <the item name from step 1>.
        Answer in the {language} language.
        Provide the output in the following JSON format:
        {most_important_topics_parser.get_format_instructions()}
    """
    answer = await answer_question(question)
    return most_important_topics_parser.parse(answer)


@app.get("/answer-question")
async def answer_user_question(
    question: str, language: SupportedLanguage = SupportedLanguage.english
):
    return {
        "answer": await answer_question(question, language),
    }
