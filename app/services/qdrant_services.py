from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
import qdrant_client
from services.chunking_services import document_chunk

def get_retriever():
    #dense vector
    dense_embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    #sparse vector
    sparse_embedding = FastEmbedSparse(model_name="Qdrant/bm25")

    db_path = "../db"
    collection_name = "financial_report"

    client = qdrant_client.QdrantClient(path=db_path)

    qdrant_store = None    
    if client.collection_exists(collection_name=collection_name):
        qdrant_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=dense_embedding,
            sparse_embedding=sparse_embedding,
            retrieval_mode=RetrievalMode.HYBRID
        )
    else:
        file_path = "../Sample-Financial-Statement.pdf"
        chunks = document_chunk(file_path=file_path)
        qdrant_store = QdrantVectorStore.from_documents(
            documents=chunks,
            collection_name=collection_name,
            embedding=dense_embedding,
            sparse_embedding=sparse_embedding,
            retrieval_mode=RetrievalMode.HYBRID,
            client=client
        )

    hybrid_retriever = qdrant_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    return hybrid_retriever

