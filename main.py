from __future__ import annotations
import json, pdfplumber, pathlib, textwrap
from typing import Tuple, Dict, Any

import gradio as gr

from agents.classificationAgent import ClassficationAgent
from agents.jsonAgent import JSONAgent
from agents.emailAgent import EmailAgent
from agents.pdfAgent import PDFAgent
from memory import Memory         

# ───────────────────────── common helpers ───────────────────────── #

def read_payload(file: gr.File | None, raw_text: str | None) -> Tuple[Any, str]:
    if file is not None and file.name:
        p = pathlib.Path(file.name)
        if p.suffix.lower() == ".pdf":
            with pdfplumber.open(p) as pdf:
                txt = "\n".join(page.extract_text() or "" for page in pdf.pages)
            return txt, p.name
        elif p.suffix.lower() == ".json":
            return json.load(open(p, "r", encoding="utf-8")), p.name
        else:    
            return open(p, "r", encoding="utf-8").read(), p.name

    if raw_text:
        return raw_text, "pasted_input.txt"
    raise gr.Error("Please upload a file or paste text.")

def choose_agent(fmt: str):
    return {
        "json":  JSONAgent(),
        "email": EmailAgent(),
        "pdf":   PDFAgent(),  
    }.get(fmt)

# ─────────────────────────── core runner ────────────────────────── #

mem = Memory()                
cls_agent = ClassficationAgent() 

def run_router(file: gr.File | None, raw_text: str | None):
    """
    1. Ingest file/text
    2. Classify → choose downstream agent
    3. Persist each step to memory
    4. Return UI-friendly dict
    """
    data, source = read_payload(file, raw_text)
    print(f"Input data: {data[:100]}... (source: {source})")
    if not data:
        raise gr.Error("No data to process. Please upload a file or paste text.")

    # 1) Classify
    decision = cls_agent.handle(data, {"source": source})
    print(f"Classifier decision: {decision}")
    fmt, intent, conf, thread_id = (
        decision["format"], decision["intent"],
        decision["confidence"], decision["thread_id"]
    )

    # 2) Route
    worker = choose_agent(fmt)
    if worker is None:
        downstream = {"warning": f"No worker agent for format '{fmt}'."}
    else:
        downstream = worker.handle(data, {"source": source, "thread_id": thread_id})

    print(f"Downstream agent output: {downstream}")

    # 3) Fetch last memory entry for provenance display
    last = mem.last(thread_id)
    log_row = dict(zip(
        ("id","thread_id","source","fmt","intent","payload","ts"), last
    )) if last else {}

    return {
        "Classifier →": decision,
        "Agent output →": downstream,
        "Memory log →": log_row
    }

# ──────────────────────────── UI layout ─────────────────────────── #

with gr.Blocks(title="Multi-Agent Router") as demo:
    gr.Markdown("# 📂 Multi-Agent Router Demo\nUpload a file **or** paste text.")
    with gr.Row(equal_height=True):
        file_in  = gr.File(label="PDF / JSON / TXT")
        text_in  = gr.Textbox(label="Or paste raw e-mail / text here",
                              lines=12, placeholder="Hi team, I'd like a quote for...")
    run_btn   = gr.Button("Run")
    out_json  = gr.JSON(label="Result")

    run_btn.click(run_router, inputs=[file_in, text_in], outputs=out_json)

if __name__ == "__main__":
    demo.launch()
