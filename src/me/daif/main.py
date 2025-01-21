from fastapi import FastAPI

from me.daif.agent.kumpel import answer_question
from me.daif.agent.language import SupportedLanguage

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "OK"}


@app.get("/suggest-predefined-questions")
async def suggest_predefined_questions(language: SupportedLanguage):
    # TODO: This is temporary, we should generate some questions dynamically.
    match language:
        case SupportedLanguage.english:
            return {
                "body": [
                    """
                For each party of the following parties:
                "AFD", "BSW", "CDU/CSU", "FDP", "The Greens", "Die Linke", "SPD"
                Tell me the stance of the party on energy. In particular the solar farms, wind farms,
                coal, wood, and fossil fuels.
                Make your answer concise and in a simple language.
                """,
                    """
                For each party of the following parties:
                "AFD", "BSW", "CDU/CSU", "FDP", "The Greens", "Die Linke", "SPD"
                Tell me the stance of the party on illegal immigration.
                Make your answer concise and in a simple language.
                """,
                    """
                For each party of the following parties:
                "AFD", "BSW", "CDU/CSU", "FDP", "The Greens", "Die Linke", "SPD"
                Tell me the stance of the party on the relations with Russia.
                Make your answer concise and in a simple language.
                """,
                    """
                Given all the knowledge you have on the parties, what could be the top
                20 questions I can ask in order to be able to make an informative
                decision on whom to vote for ?
                """,
                ]
            }
        case SupportedLanguage.german:
            return {
                "body": [
                    """
                    Für jede der folgenden Parteien:
                    "AFD", "BSW", "CDU/CSU", "FDP", "Die Grünen", "Die Linke", "SPD"
                    Erklären Sie mir die Haltung der Partei zur Energiepolitik. Insbesondere zu Solarparks, 
                    Windkraftanlagen, Kohle, Holz und fossilen Brennstoffen.
                    Machen Sie Ihre Antwort prägnant und in einfacher Sprache.
                    """,
                    """
                    Für jede der folgenden Parteien:
                    "AFD", "BSW", "CDU/CSU", "FDP", "Die Grünen", "Die Linke", "SPD"
                    Erklären Sie mir die Haltung der Partei zur illegalen Einwanderung.
                    Machen Sie Ihre Antwort prägnant und in einfacher Sprache.
                    """,
                    """
                    Für jede der folgenden Parteien:
                    "AFD", "BSW", "CDU/CSU", "FDP", "Die Grünen", "Die Linke", "SPD"
                    Erklären Sie mir die Haltung der Partei zu den Beziehungen zu Russland.
                    Machen Sie Ihre Antwort prägnant und in einfacher Sprache.
                    """,
                    """
                    Angesichts aller Kenntnisse über die Parteien, welche wären die 20 wichtigsten Fragen, die ich 
                    stellen könnte, um eine fundierte Entscheidung darüber zu treffen, wen ich wählen soll?
                    """,
                ]
            }


@app.get("/answer-question")
async def answer_user_question(question: str):
    return {
        "body": await answer_question(question),
    }
