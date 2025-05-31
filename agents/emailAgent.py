import uuid

from pydantic import BaseModel
from askAI import ask_ai
from agents.baseAgent import BaseAgent

class EmailSchema(BaseModel):
    sender: str
    intent: str  # invoice|rfq|complaint|regulation|other
    urgency: str  # low/medium/high
    summary: str  # ≤30 words

_SYS = """Extract sender, intent (invoice|rfq|complaint|regulation|other),
and urgency (low/medium/high). Respond strictly as JSON with keys:
sender,intent,urgency,summary (≤30 words)."""

class EmailAgent(BaseAgent):
    def handle(self, input_text: str, meta: dict) -> dict:
        try:
            res = ask_ai(
                prompt=input_text,
                sys_prompt=_SYS,
                schema=EmailSchema,
            )
            
            thread_id = meta.get("thread_id") or str(uuid.uuid4())
            self.memory.write(thread_id=thread_id,
                              source=meta["source"],
                              fmt="email",
                              intent=res["intent"],
                              payload=res)
            res["thread_id"] = thread_id
            return res
        except Exception as e:
            print(f"Error in EmailAgent: {e}")
            return {"error": str(e)}