from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from services.qdrant_services import get_retriever
from core.exceptions import LLMGenerationError, VectorDBError, DocumentParserError

async def generate_response(query: str):
    try:
        llm = ChatOpenAI(model="gpt-4o")

        prompt = PromptTemplate.from_template(
        """you are a helpful assistent try to answer the user query with the help of 
        given context if the context is not available or related to user query say sorry i am not able to help you with your query
        context: {context}
        query: {query}
        """,
        )

        retriever = await get_retriever()
        retrieved_docs = await retriever.ainvoke(query)
        context = _join_docs(docs=retrieved_docs)
        formatted_prompt = prompt.format(context=context, query=query)

        response = await llm.ainvoke(formatted_prompt)
        return response.content
    except (DocumentParserError, VectorDBError, LLMGenerationError):
        raise
    except Exception as e:
        raise LLMGenerationError(f"Failed to generate LLM response: {str(e)}")

def _join_docs(docs: list):
    final_context = "\n\n".join([doc.page_content for doc in docs])
    return final_context
