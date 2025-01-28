import os

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

from me.daif.agent.language import SupportedLanguage

FAISS_INDEX_NAME = "local.db"


async def answer_question(
    question: str, language: SupportedLanguage, chat_history: list[str]
) -> str:
    vectorstore = await _load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 30, "fetch_k": 60, "lambda_mult": 0.5},
    )

    llm = ChatOpenAI(temperature=0)

    # Contextualize question
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_system_prompt = (
        "You are an assistant for question-answering tasks. Use "
        "the following pieces of retrieved context to answer the "
        "question. If you don't know the answer, just say that you "
        "don't know."
        "\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    question = f"""
        {question}
        Translate your answer in the {language} language.
    """
    response = rag_chain.invoke({"input": question, "chat_history": chat_history})
    answer = response["answer"]

    return answer


async def _load_vectorstore() -> FAISS:
    embeddings = OpenAIEmbeddings()

    if os.path.isdir(FAISS_INDEX_NAME):
        return FAISS.load_local(
            FAISS_INDEX_NAME,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    documents = []
    for file in os.listdir("documents"):
        filename = os.fsdecode(file)
        if filename.endswith(".pdf"):
            party, _ = filename.split(".")
            loader = PyPDFLoader(file_path=f"documents/{filename}")
            party_documents = loader.load()
            for doc in party_documents:
                doc.metadata["party"] = party
                documents.append(doc)
            print(f"Loaded {file}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(documents=documents)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(FAISS_INDEX_NAME)
    return vectorstore
