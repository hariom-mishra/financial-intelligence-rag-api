from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import AsyncQdrantClient
from services.chunking_services import document_chunk
from core.exceptions import VectorDBError, DocumentParserError
from core.setttings import settings

async def get_retriever():
    try:
        # dense vector
        dense_embedding = OpenAIEmbeddings(model="text-embedding-3-small")

        # sparse vector
        sparse_embedding = FastEmbedSparse(model_name="Qdrant/bm25")

        collection_name = "financial_report"

        # Connect to Qdrant Cloud
        client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

        collection_exists = await client.collection_exists(collection_name=collection_name)

        if collection_exists:
            # Collection already populated — connect directly, no re-upload
            qdrant_store = QdrantVectorStore(
                client=client,
                collection_name=collection_name,
                embedding=dense_embedding,
                sparse_embedding=sparse_embedding,
                retrieval_mode=RetrievalMode.HYBRID
            )
        else:
            # First run — chunk and upload documents to Qdrant Cloud
            file_path = "../Sample-Financial-Statement.pdf"
            chunks = document_chunk(file_path=file_path)
            qdrant_store = await QdrantVectorStore.afrom_documents(
                documents=chunks,
                collection_name=collection_name,
                embedding=dense_embedding,
                sparse_embedding=sparse_embedding,
                retrieval_mode=RetrievalMode.HYBRID,
                async_client=client
            )

        hybrid_retriever = qdrant_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        return hybrid_retriever
    except (DocumentParserError, VectorDBError):
        raise
    except Exception as e:
        raise VectorDBError(f"Vector database operation failed: {str(e)}")


