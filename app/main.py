from dotenv import load_dotenv
from services.llm_generator import generate_response

load_dotenv()

res = generate_response("What was the total operating income and net revenue for Q3?")

print(res)

