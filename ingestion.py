from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFDirectoryLoader

INDEX_NAME = "wahlkumpel-2025"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def ingest_docs():
    loader = PyPDFDirectoryLoader(path="documents/")
    raw_documents = loader.load()
    print(f"Loaded: {len(raw_documents)}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)

    print(f"Going to add {len(documents)} to Pinecone.")
    PineconeVectorStore.from_documents(
        documents,
        embeddings,
        index_name=INDEX_NAME,
    )
    print("**Loading to vectorstore done**")


if __name__ == "__main__":
    ingest_docs()
