from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from agents.memory import memory
from utils.logger import get_logger

logger = get_logger(__name__)

class RefinerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        with open("models/prompts/refine.txt", "r") as f:
            template = f.read()
        self.prompt = PromptTemplate.from_template(template)

    def refine(self, email: str, draft: str, feedback: str, email_id: str) -> str:
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({
                "email": email,
                "draft": draft,
                "feedback": feedback
            }).content.strip()
            memory.add_feedback(email_id, feedback, draft)
            logger.info(f"Refined draft for {email_id}")
            return result
        except Exception as e:
            logger.error(f"Refinement failed: {e}")
            return draft	