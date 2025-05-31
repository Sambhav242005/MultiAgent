from pydantic import BaseModel
from askAI import ask_ai
from agents.baseAgent import BaseAgent
import json, uuid

class TypesEvent(BaseModel):
    format: str
    intent: str
    confidence: float
    thread_id: str | None = None

class ClassficationAgent(BaseAgent):

    def handle(self,input_text,meta):

        _SYS_PROMPT = """
        You are a strict classifier.  
        Return ONLY JSON exactly matching this schema:
        {"format":"pdf|json|email",
        "intent":"invoice|rfq|complaint|regulation|other",
        "confidence":0-1}
        """
        try:
            response = ask_ai(
                            prompt=input_text[:150],
                            sys_prompt=_SYS_PROMPT,
                            schema=TypesEvent,
                        )
            
            print(f"AI Response in ClassficationAgent: {response}")

            thread_id = str(uuid.uuid4())
            self.memory.write(thread_id=thread_id,
                              source=meta["source"],
                              fmt=response["format"],
                              intent=response["intent"],
                              payload=response)
            response["thread_id"] = thread_id
            return response
        except Exception as e:
            print(f"Error in typeIdentifyAgent: {e}")
            return "unknown"
        
        

# Example usage:
if __name__ == "__main__":
    input_text = """This is a sample email from
    from:sam@gmail.com
    to:sa1@gmail.com
    message:Hello, this is a test email."""
    result = ClassficationAgent().handle(input_text=input_text,meta= {"source": "example_source"})
    print(f"Identified type: {result}")