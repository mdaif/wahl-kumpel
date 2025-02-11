from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from me.daif.agent.language import SupportedLanguage

INDEX_NAME = "wahlkumpel-2025"


async def answer_question(
    query: str, language: SupportedLanguage, chat_history: list[tuple[str, str]]
):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
    chat = ChatOpenAI(verbose=True, temperature=0)

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    history_aware_retriever = create_history_aware_retriever(
        llm=chat,
        retriever=docsearch.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 30, "fetch_k": 60, "lambda_mult": 0.5},
        ),
        prompt=rephrase_prompt,
    )
    qa = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=stuff_documents_chain,
    )
    query = f"""
        {query}
        
        Your final answer should be in the {language} language.
    """
    result = qa.invoke(input={"input": query, "chat_history": chat_history})
    return result["answer"]
