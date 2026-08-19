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

class DatabaseConnectionError(RAGException):
    def __init__(self, message: str = "Failed to connect to the db"):
        super().__init__(message, status_code=500)

class UserAlreadyExistsError(RAGException):
    """Raised when a signup is attempted with an already-registered email"""
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists.", status_code=409)

class InvalidCredentialsError(RAGException):
    """Raised when login credentials are incorrect"""
    def __init__(self):
        super().__init__("Invalid email or password.", status_code=401)