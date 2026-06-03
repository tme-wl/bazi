from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .analyzer import analyze_chart
from .calendar import build_chart
from .parser import ParseError, parse_birth_text
from .prompt_builder import build_llm_prompt
from .renderer import render_html, write_html


app = FastAPI(title="Bazi Mingyi")


class GenerateRequest(BaseModel):
    text: str


@app.post("/generate")
def generate(req: GenerateRequest) -> dict[str, str]:
    try:
        birth = parse_birth_text(req.text)
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    chart = build_chart(birth)
    analysis = analyze_chart(chart)
    filename = f"mingzhu-{uuid4().hex[:8]}.html"
    output_path = write_html(analysis, Path("outputs") / filename)
    prompt_filename = filename.replace(".html", ".md")
    prompt_path = Path("outputs") / prompt_filename
    prompt_path.write_text(build_llm_prompt(analysis), encoding="utf-8")
    return {
        "bazi": chart.bazi,
        "summary": analysis.summary,
        "html_path": str(output_path.resolve()),
        "prompt_path": str(prompt_path.resolve()),
        "preview_url": f"/preview/{filename}",
    }


@app.post("/preview", response_class=HTMLResponse)
def preview(req: GenerateRequest) -> str:
    try:
        birth = parse_birth_text(req.text)
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return render_html(analyze_chart(build_chart(birth)))


@app.get("/preview/{filename}", response_class=HTMLResponse)
def preview_file(filename: str) -> str:
    path = Path("outputs") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    return path.read_text(encoding="utf-8")
