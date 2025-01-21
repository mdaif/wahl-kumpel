from me.daif.agent.kumpel import answer_question


def main():
    questions = [
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

    for question in questions:
        print(f"Question: {question}\n\n")
        answer = answer_question(question)
        print(f"Answer: {answer}")
        print("#" * 100)
