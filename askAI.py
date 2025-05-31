from __future__ import annotations

import json
import os
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)   # concrete schema class to return


def ask_ai(
    prompt: str,
    *,
    schema: Type[T],                       # e.g. MySchema (a BaseModel subclass)
    model: str = "gpt-4.1-nano",            # any “JSON mode”-capable model
    sys_prompt: str | None = None,
    max_tokens: int = 256,
    temperature: float = 0.7,
) -> T:
    if sys_prompt is None:
        # Minimal system instruction: model *must* output valid JSON only.
        sys_prompt = (
            "You are a helpful assistant. "
            "Reply *only* with valid JSON that obeys the schema I give you."
        )

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},  # “JSON mode”
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # --- parse and validate -------------------------------------------------
    json_text = response.choices[0].message.content            # str
    raw = json.loads(json_text)                                # dict
    return schema(**raw).model_dump(mode="json")                                       # ↩︎ typed object


