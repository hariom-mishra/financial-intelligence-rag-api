from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams, SparseIndexParams
from services.chunking_services import document_chunk
from core.exceptions import VectorDBError, DocumentParserError
from core.setttings import settings


def _get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )


def _collection_name(user_id: int) -> str:
    """Deterministic per-user Qdrant collection name."""
    return f"user_{user_id}_docs"


async def create_user_collection(user_id: int) -> None:
    """
    Pre-create a hybrid (dense + sparse) Qdrant collection for a new user.
    Called once at signup. Safe to call if collection already exists.
    """
    try:
        client = _get_qdrant_client()
        name = _collection_name(user_id)

        exists = await client.collection_exists(collection_name=name)
        if exists:
            return

        await client.create_collection(
            collection_name=name,
            vectors_config={
                "dense": VectorParams(size=1536, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            },
        )
    except Exception as e:
        raise VectorDBError(f"Failed to create collection for user {user_id}: {str(e)}")


async def get_retriever(user_id: int):
    """
    Build and return a hybrid (BM25 + dense) retriever scoped to
    the authenticated user's Qdrant collection.
    """
    try:
        dense_embedding = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY,
        )
        sparse_embedding = FastEmbedSparse(model_name="Qdrant/bm25")
        collection_name = _collection_name(user_id)

        client = _get_qdrant_client()

        collection_exists = await client.collection_exists(collection_name=collection_name)

        if collection_exists:
            qdrant_store = QdrantVectorStore(
                client=client,
                collection_name=collection_name,
                embedding=dense_embedding,
                sparse_embedding=sparse_embedding,
                retrieval_mode=RetrievalMode.HYBRID,
            )
        else:
            raise VectorDBError(
                f"No documents indexed yet for this user. "
                f"Please upload a document first."
            )

        hybrid_retriever = qdrant_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )

        return hybrid_retriever
    except (DocumentParserError, VectorDBError):
        raise
    except Exception as e:
        raise VectorDBError(f"Vector database operation failed: {str(e)}")


async def index_documents(user_id: int, chunks: list):
    """
    Index documents into the user's Qdrant collection.
    """
    try:
        dense_embedding = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY,
        )
        sparse_embedding = FastEmbedSparse(model_name="Qdrant/bm25")
        collection_name = _collection_name(user_id)
        client = _get_qdrant_client()

        await QdrantVectorStore.afrom_documents(
            documents=chunks,
            collection_name=collection_name,
            embedding=dense_embedding,
            sparse_embedding=sparse_embedding,
            retrieval_mode=RetrievalMode.HYBRID,
            async_client=client,
        )
    except Exception as e:
        raise VectorDBError(f"Failed to index documents: {str(e)}")
