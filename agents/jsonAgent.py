from pydantic import BaseModel, ValidationError
from agents.baseAgent import BaseAgent
from askAI import ask_ai

class JSONSchema(BaseModel):
    good: dict
    bad: list

class JSONAgent(BaseAgent):
    def handle(self, data: dict,schema : BaseModel, meta: dict):
        try:
            good = schema(**data).model_dump()
            bad = []
        except ValidationError as e:
            good = {}
            bad = []
            res=ask_ai(
                prompt=data,
                sys_prompt="You are a strict validator. Return only List with keys 'anomalies' and 'missing field' .",
                schema=BaseModel,
            )
            if res:
                if isinstance(res, list):
                    bad = res
                else:
                    bad = [res]
            else:
                bad = ["Unknown error in JSON validation"]

        self.memory.write(thread_id=meta["thread_id"],
                          source=meta["source"],
                          fmt="json",
                          intent=meta["intent"],
                          payload={"good": good,
                                   "bad": bad})
        return {"ok": not bad, "good": good,
                "bad": bad}
