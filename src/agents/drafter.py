from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from agents.memory import memory
from utils.logger import get_logger

logger = get_logger(__name__)

class DrafterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        with open("models/prompts/draft.txt", "r") as f:
            template = f.read()
        self.prompt = PromptTemplate.from_template(template)

    def draft(self, email: str, email_id: str) -> str:
        similar = memory.retrieve_similar(email, n=2)
        feedback = "\n".join([f"Past: {m['feedback']}" for m in similar]) if similar else "None"
        
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"email": email, "feedback": feedback}).content.strip()
            logger.info(f"Draft created for {email_id}")
            return result
        except Exception as e:
            logger.error(f"Drafting failed: {e}")
            return "Sorry, I couldn't generate a reply."