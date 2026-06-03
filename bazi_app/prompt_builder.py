from __future__ import annotations

import json

from .analyzer import load_prompt
from .models import Analysis


def build_llm_prompt(analysis: Analysis) -> str:
    """Build a complete model prompt from the editable Markdown rule file."""
    chart = analysis.chart
    facts = {
        "raw_input": chart.birth.raw_text,
        "calendar": chart.birth.calendar,
        "birth_time": chart.birth.birth_dt.isoformat(sep=" "),
        "gender": chart.birth.gender,
        "bazi": chart.bazi,
        "pillars": {
            "year": chart.year.ganzhi,
            "month": chart.month.ganzhi,
            "day": chart.day.ganzhi,
            "hour": chart.hour.ganzhi,
        },
        "day_master": chart.day_master,
        "day_element": chart.day_element,
        "element_scores": analysis.element_scores,
        "pattern": analysis.pattern,
        "useful": analysis.useful,
        "avoid": analysis.avoid,
        "relations": analysis.relations,
        "luck_cycles": analysis.luck_cycles,
    }
    return (
        f"{load_prompt()}\n\n"
        "## 本次命盘结构化数据\n\n"
        "请严格依据上方 Markdown 规则，结合下列 JSON 数据生成命书分析文本，"
        "再交由 HTML 渲染器输出。\n\n"
        "```json\n"
        f"{json.dumps(facts, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )
