from docling.document_converter import DocumentConverter
from pathlib import Path

def parse_document(file_path: str):
    #path create and check 
    path = Path(file_path)
    if(not path.exists()):
        raise Exception("path doesnt exists")

    #convert to markdown format
    converter = DocumentConverter()
    result = converter.convert(path)
    docs = result.document.export_to_markdown()
    
    return docs






    