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

from me.daif.agent.language import SupportedLanguage

FAISS_INDEX_NAME = "local.db"


async def answer_question(
    question: str, language: SupportedLanguage | None = SupportedLanguage.english
) -> str:
    vectorstore = await _load_vectorstore()

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(
        ChatOpenAI(temperature=0), retrieval_qa_chat_prompt
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 30, "fetch_k": 60, "lambda_mult": 0.5},
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    if language:
        question = f"""
            {question}
            Please translate your answer in the {language} language.
        """
    response = retrieval_chain.invoke({"input": question})
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
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?"],
    )
    documents = text_splitter.split_documents(documents=documents)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(FAISS_INDEX_NAME)
    return vectorstore
