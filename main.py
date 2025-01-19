import os

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS


def main():
    print("Loading the electoral programs")

    vectorstore = _load_vectorstore()

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(
        ChatOpenAI(temperature=0), retrieval_qa_chat_prompt
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 30, "fetch_k": 60, "lambda_mult": 0.5},
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

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
        response = retrieval_chain.invoke({"input": question})
        answer = response["answer"]
        print(f"Answer: {answer}")
        print("#" * 100)


def _load_vectorstore() -> FAISS:
    embeddings = OpenAIEmbeddings()

    if os.path.isdir("local.db"):
        return FAISS.load_local(
            "local.db",
            embeddings,
            allow_dangerous_deserialization=True,
        )

    documents = []
    for file in os.listdir("./documents"):
        filename = os.fsdecode(file)
        if filename.endswith(".pdf"):
            party, _ = filename.split(".")
            loader = PyPDFLoader(file_path=f"./documents/{filename}")
            party_documents = loader.load()
            for doc in party_documents:
                doc.metadata["party"] = party
                documents.append(doc)
            print(f"Loaded {file}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?"],
    )
    documents = text_splitter.split_documents(documents=documents)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local("local.db")
    return vectorstore


if __name__ == "__main__":
    main()
