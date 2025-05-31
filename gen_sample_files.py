#!/usr/bin/env python3
"""
Generate synthetic input files for the multi-agent-router demo.

 • Invoices      →  invoice_EMAIL_<N>.pdf   (PDF)
 • RFQs          →  rfq_<N>.json            (JSON)
 • Complaints    →  complaint_email_<N>.txt (plain-text “e-mail”)

Usage
-----
python generate_samples.py --out-dir sample_inputs --count 5 --seed 42
"""

from __future__ import annotations
import argparse, json, os, random, textwrap
from datetime import date
from pathlib import Path

from faker import Faker
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen.canvas import Canvas

fake = Faker()

# ───────────────────────── helpers ───────────────────────── #

def _invoice_pdf(path: Path):
    """Write a one-page PDF invoice."""
    canvas = Canvas(str(path), pagesize=LETTER)
    w, h = LETTER
    canvas.setTitle("Invoice")

    # Header
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(40, h - 60, "INVOICE")
    canvas.setFont("Helvetica", 10)
    canvas.drawString(40, h - 80, f"Invoice #: {fake.unique.random_int(1000, 9999)}")
    canvas.drawString(40, h - 95, f"Date: {date.today().isoformat()}")

    # Bill-to
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(40, h - 125, "Bill To:")
    canvas.setFont("Helvetica", 10)
    for i, line in enumerate(fake.address().splitlines()):
        canvas.drawString(40, h - 140 - i * 12, line)

    # Table header
    canvas.setFont("Helvetica-Bold", 10)
    y = h - 200
    canvas.drawString(40, y, "Description")
    canvas.drawString(400, y, "Amount (USD)")
    canvas.line(40, y - 3, 550, y - 3)

    # Line items
    total = 0.0
    for _ in range(random.randint(2, 5)):
        y -= 18
        desc = fake.catch_phrase()
        amount = round(random.uniform(150, 1200), 2)
        total += amount
        canvas.setFont("Helvetica", 10)
        canvas.drawString(40, y, desc[:50])
        canvas.drawRightString(500, y, f"{amount:,.2f}")

    # Total
    y -= 25
    canvas.setFont("Helvetica-Bold", 11)
    canvas.line(350, y + 5, 550, y + 5)
    canvas.drawRightString(500, y - 2, f"TOTAL  {total:,.2f}")

    canvas.save()

def _rfq_json(path: Path):
    """Write a Request-for-Quotation JSON payload."""
    product = fake.word().title()
    payload = {
        "rfq_id": fake.unique.random_int(10000, 99999),
        "request_date": date.today().isoformat(),
        "company": fake.company(),
        "contact": {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number()
        },
        "items": [
            {
                "product_code": f"{product[:3].upper()}{random.randint(10,99)}",
                "description": f"{product} – {fake.bs()}",
                "quantity": random.randint(10, 500)
            } for _ in range(random.randint(1, 3))
        ],
        "notes": fake.sentence()
    }
    path.write_text(json.dumps(payload, indent=2))

def _complaint_email(path: Path):
    """Write a simple customer-complaint e-mail."""
    subject = f"Complaint about order #{fake.random_int(1000, 9999)}"
    body = textwrap.dedent(f"""\
        From: {fake.name()} <{fake.email()}>
        To: support@example.com
        Subject: {subject}

        Hello,

        I am disappointed with the product I received on {fake.date_this_year()}.
        It arrived damaged and is not functioning as advertised. Please advise on
        how I can obtain a replacement or a full refund.

        Sincerely,
        {fake.name()}
    """)
    path.write_text(body)

# ─────────────────────────── main ────────────────────────── #

def main(out_dir: str, count: int, seed: int | None):
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i in range(1, count + 1):
        _invoice_pdf(out / f"invoice_email_{i}.pdf")
        _rfq_json   (out / f"rfq_{i}.json")
        _complaint_email(out / f"complaint_email_{i}.txt")

    print(f"✅  Generated {count*3} sample files in {out.resolve()}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="sample_inputs",
                    help="Target directory (default: sample_inputs/)")
    ap.add_argument("--count", type=int, default=3,
                    help="How many of each type to create (default: 3)")
    ap.add_argument("--seed", type=int, default=None,
                    help="Random seed for reproducibility")
    main(**vars(ap.parse_args()))
