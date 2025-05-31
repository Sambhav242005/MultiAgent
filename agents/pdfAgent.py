import uuid
from json import JSONDecodeError
from typing import Any, Dict

from pydantic import BaseModel, ValidationError

from agents.baseAgent import BaseAgent
from askAI import ask_ai          # ← earlier helper that returns a Pydantic instance
from memory import Memory         # the thread-local version shown earlier


class PDFSchema(BaseModel):
    title: str
    raw_text: str
    intent: str                    # invoice · rfq · complaint · regulation · other
    sender: str | None = None      # optional


class PDFAgent(BaseAgent):

    def handle(self, pdf_text: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Parse `pdf_text`, log the result, and return the structured payload."""
        thread_id = meta.get("thread_id") or str(uuid.uuid4())

        try:
            res = ask_ai(            
                prompt=pdf_text,
                schema=PDFSchema,
                sys_prompt=(
                    "You are a strict PDF extractor. "
                    "Reply *only* with valid JSON containing keys "
                    '`title`, `raw_text`, `intent`, and optional `sender`.'
                ),
                max_tokens=512,                         # keep plenty of room
            )

        except Exception as e:
            # Bubble up or convert to your framework’s error type
            raise RuntimeError(f"PDFAgent validation failed: {e}") from e
        
        

        # Convert to plain dict so we can mutate / serialize
        payload = res # type: ignore[return-value]
        if not payload.get("intent"):
            raise ValueError("Intent is required in PDF processing.")
        payload["thread_id"] = thread_id

        # Persist to SQLite (thread-local connection → no cross-thread error)
        self.memory.write(
            thread_id=thread_id,
            source=meta.get("source", "<unknown>"),
            fmt="pdf",
            intent=payload["intent"],
            payload=payload,
        )

        return payload
