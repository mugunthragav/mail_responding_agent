from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils.logger import get_logger

logger = get_logger(__name__)

class ClassifierAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        with open("models/prompts/classify.txt", "r") as f:
            template = f.read()
        self.prompt = PromptTemplate.from_template(template)

    def classify(self, email: str) -> str:
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"email": email}).content.strip()
            logger.info(f"Classified: {result}")
            return result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "UNKNOWN"