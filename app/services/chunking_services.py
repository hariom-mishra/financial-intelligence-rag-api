from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from services.document_parser import parse_document
from core.exceptions import DocumentParserError

def document_chunk(file_path: str):
    try:
        docs = parse_document(file_path=file_path)
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        text_splitter1 = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        structural_chunks = text_splitter1.split_text(docs)

        text_splitter2 = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", r"(?<=\. )", " ", ""]
        )

        final_chunks = text_splitter2.split_documents(structural_chunks)
        return final_chunks
    except DocumentParserError:
        raise
    except Exception as e:
        raise DocumentParserError(f"Failed to chunk document: {str(e)}")