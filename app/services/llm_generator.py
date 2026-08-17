from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from services.qdrant_services import get_retriever

def generate_response(query: str):
    llm = ChatOpenAI(model="gpt-4o")

    prompt = PromptTemplate.from_template(
    """you are a helpful assistent try to answer the user query with the help of 
    given context if the context is not available or related to user query say sorry i am not able to help you with your query
    context: {context}
    query: {query}
    """,
    )

    retriever = get_retriever()
    retrieved_docs = retriever.invoke(query)
    context = _join_docs(docs=retrieved_docs)
    formatted_prompt = prompt.format(context=context, query=query)

    response = llm.invoke(formatted_prompt)

    return response.content


def _join_docs(docs: list):
    final_context = "\n\n".join([doc.page_content for doc in docs])
    return final_context
