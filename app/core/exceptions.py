class RAGException(Exception):
    """Base exception class for RAG application errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DocumentParserError(RAGException):
    """Raised when document reading or conversion fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class VectorDBError(RAGException):
    """Raised when vector database connection or indexing fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class LLMGenerationError(RAGException):
    """Raised when LLM response generation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)
