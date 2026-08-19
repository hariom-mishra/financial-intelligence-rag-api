from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from services.qdrant_services import get_retriever
from core.exceptions import LLMGenerationError, VectorDBError, DocumentParserError
from core.setttings import settings

async def generate_response(query: str, user_id: int) -> str:
    """
    Run the hybrid-search RAG pipeline for a specific user:
      1. Retrieve relevant chunks from the user's Qdrant collection.
      2. Format a prompt with context + query.
      3. Call the LLM and return the response.
    """
    try:
        llm = ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)

        prompt = PromptTemplate.from_template(
            """You are a financial intelligence assistant. Answer the user's query 
using only the provided context. If the context doesn't contain relevant 
information, say: "I'm sorry, I don't have enough information in your documents to answer that."

Context:
{context}

Query: {query}

Answer:""",
        )

        retriever = await get_retriever(user_id=user_id)
        retrieved_docs = await retriever.ainvoke(query)
        context = _join_docs(docs=retrieved_docs)
        formatted_prompt = prompt.format(context=context, query=query)

        response = await llm.ainvoke(formatted_prompt)
        return response.content
    except (DocumentParserError, VectorDBError, LLMGenerationError):
        raise
    except Exception as e:
        raise LLMGenerationError(f"Failed to generate LLM response: {str(e)}")


def _join_docs(docs: list) -> str:
    return "\n\n".join([doc.page_content for doc in docs])
