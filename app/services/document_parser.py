from docling.document_converter import DocumentConverter
from pathlib import Path
from core.exceptions import DocumentParserError

def parse_document(file_path: str):
    try:
        #path create and check 
        path = Path(file_path)
        if(not path.exists()):
            raise DocumentParserError(f"File path does not exist: {file_path}")

        #convert to markdown format
        converter = DocumentConverter()
        result = converter.convert(path)
        docs = result.document.export_to_markdown()
        return docs
    except DocumentParserError:
        raise
    except Exception as e:
        raise DocumentParserError(f"Failed to parse document: {str(e)}")






    