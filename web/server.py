"""
FastAPI backend for Bazi Mingyi.
Integrates core skill for chart calculation / rule analysis.
Supports LLM enhancement via OpenAI-compatible API when BAZI_API_KEY is set.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from skill.analyzer import analyze_chart
from skill.calendar import build_chart
from skill.constants import STEM_ELEMENT, BRANCH_ELEMENT, STEMS, BRANCHES, ELEMENTS
from skill.models import BirthInput
from skill.prompt_builder import build_llm_prompt

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
)
logger = logging.getLogger("bazi.web")

# ---------------------------------------------------------------------------
# English translation mappings
# ---------------------------------------------------------------------------

STEM_EN: dict[str, str] = {
    "甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding",
    "戊": "Wu", "己": "Ji", "庚": "Geng", "辛": "Xin",
    "壬": "Ren", "癸": "Gui",
}

BRANCH_EN: dict[str, str] = {
    "子": "Zi", "丑": "Chou", "寅": "Yin", "卯": "Mao",
    "辰": "Chen", "巳": "Si", "午": "Wu", "未": "Wei",
    "申": "Shen", "酉": "You", "戌": "Xu", "亥": "Hai",
}

BRANCH_ANIMAL_EN: dict[str, str] = {
    "子": "Rat", "丑": "Ox", "寅": "Tiger", "卯": "Rabbit",
    "辰": "Dragon", "巳": "Snake", "午": "Horse", "未": "Goat",
    "申": "Monkey", "酉": "Rooster", "戌": "Dog", "亥": "Pig",
}

ELEMENT_EN: dict[str, str] = {
    "木": "Wood", "火": "Fire", "土": "Earth", "金": "Metal", "水": "Water",
}

PATTERN_EN: dict[str, str] = {
    "身强格": "Strong Body",
    "身弱格": "Weak Body",
    "平衡格": "Balanced",
    "从格": "Following",
    "专旺格": "Special",
}

GENDER_ZH: dict[str, str] = {"male": "男", "female": "女"}
GENDER_EN: dict[str, str] = {"male": "Male", "female": "Female"}

# ---------------------------------------------------------------------------
# Helper helpers
# ---------------------------------------------------------------------------


def _stem_en(stem: str) -> str:
    return STEM_EN.get(stem, stem)


def _branch_en(branch: str) -> str:
    return BRANCH_EN.get(branch, branch)


def _branch_animal_en(branch: str) -> str:
    return BRANCH_ANIMAL_EN.get(branch, branch)


def _element_en(element: str) -> str:
    return ELEMENT_EN.get(element, element)


def _element_list_en(elements: list[str]) -> list[str]:
    return [_element_en(e) for e in elements]


def _bazi_en(bazi_cn: str) -> str:
    """Convert '辛未 甲午 丁亥 辛丑' -> 'Xin-Wei Jia-Wu Ding-Hai Xin-Chou'"""
    parts = bazi_cn.split()
    translated = []
    for p in parts:
        if len(p) >= 2:
            s = _stem_en(p[0])
            b = _branch_en(p[1])
            translated.append(f"{s}-{b}")
        else:
            translated.append(p)
    return " ".join(translated)


def _ganzhi_en(ganzhi: str) -> str:
    """Convert '丙申' -> 'Bing-Shen'"""
    if len(ganzhi) >= 2:
        return f"{_stem_en(ganzhi[0])}-{_branch_en(ganzhi[1])}"
    return ganzhi


# ---------------------------------------------------------------------------
# Rule-based English section generators (fallback when no LLM)
# ---------------------------------------------------------------------------

_PERSONALITY_ZH_TEMPLATES: dict[str, str] = {
    "木": "日主属木，性格仁慈宽厚，有向上生长之志。木性条达，处事有原则、有韧性，但有时过于刚直，缺乏灵活变通。宜培养水之智慧，刚柔并济。",
    "火": "日主属火，热情开朗，积极主动，富有感染力。火性炎上，做事有冲劲、有魄力，但有时急躁冲动，缺乏耐心持久。宜培养木之涵养，以柔克刚。",
    "土": "日主属土，敦厚诚实，稳重可靠，有包容之心。土性厚重，做事踏实、有担当，但有时过于保守固执，缺乏变通。宜培养火之热情，开阔格局。",
    "金": "日主属金，果敢决断，意志坚定，追求卓越。金性刚硬，做事讲原则、重效率，但有时过于严苛，缺少人情味。宜培养水之柔和，圆融处世。",
    "水": "日主属水，智慧灵动，善于应变，有深邃的洞察力。水性润下，处事灵活、善于沟通，但有时过于善变随波逐流，缺乏定力。宜培养土之稳重，扎根务实。",
}

_PERSONALITY_EN_TEMPLATES: dict[str, str] = {
    "Wood": "Day Master belongs to Wood — benevolent, generous, with a drive for growth and expansion. Wood is flexible yet principled, persistent but sometimes too rigid. Cultivate the wisdom of Water to balance firmness with adaptability.",
    "Fire": "Day Master belongs to Fire — passionate, outgoing, proactive and charismatic. Fire blazes upward with drive and boldness, but can be impatient and impulsive. Cultivate the nurture of Wood to temper intensity with grace.",
    "Earth": "Day Master belongs to Earth — honest, steady, reliable and包容. Earth is厚重 and dependable, but can be overly conservative and resistant to change. Cultivate the warmth of Fire to broaden perspective.",
    "Metal": "Day Master belongs to Metal — decisive, strong-willed, striving for excellence. Metal is principled and efficient, but can be harsh and lack interpersonal warmth. Cultivate the gentleness of Water for rounded interactions.",
    "Water": "Day Master belongs to Water — wise, adaptive, with deep insight and perception. Water flows with flexibility and good communication, but can be too changeable and lack consistency. Cultivate the stability of Earth for grounded pragmatism.",
}

_RELATIONSHIPS_ZH_TEMPLATE = (
    "感情婚姻以日支为配偶宫，综合五行生克与十神关系判断。"
    "日主五行与配偶宫五行之间的生克关系影响感情的和谐程度。"
    "命局中财官星的配置与位置，反映了感情观念和婚姻节奏。"
    "相处宜少急躁，多沟通，重大决定应避开情绪高点。"
)

_RELATIONSHIPS_EN_TEMPLATE = (
    "Relationships are analyzed through the Day Branch (spouse palace) combined with elemental interactions "
    "and the Ten Gods. The elemental relationship between the Day Master and the spouse palace influences "
    "partnership harmony. The configuration of Wealth and Officer stars reflects relationship values and "
    "marriage timing. Foster open communication and avoid major decisions during emotional peaks."
)


def _make_sections_rule(analysis: Any, chart: Any) -> dict[str, str]:
    """Build the 14-section dict from rule-based analysis (no LLM)."""
    day_el = chart.day_element
    summary = analysis.summary  # already generated by analyzer

    personality_zh = _PERSONALITY_ZH_TEMPLATES.get(day_el, "日主性格特征需结合具体命局综合判断。")
    personality_en = _PERSONALITY_EN_TEMPLATES.get(_element_en(day_el), "Personality analysis requires comprehensive chart interpretation.")

    career_zh = analysis.sections.get("career", "事业发展需结合大运流年综合判断。")
    wealth_zh = analysis.sections.get("wealth", "财富运势需结合大运流年综合分析。")
    health_zh = analysis.sections.get("health", "健康以五行平衡为要，注意生活规律与定期体检。")
    advice_zh = analysis.sections.get("advice", "总论以平衡五行为要，宜补喜用、避忌神。")

    # Basic English fallback translations for rule-based mode
    useful_str = "、".join(analysis.useful) if analysis.useful else "-"
    avoid_str = "、".join(analysis.avoid) if analysis.avoid else "-"
    useful_en_str = ", ".join(_element_list_en(analysis.useful)) if analysis.useful else "-"
    avoid_en_str = ", ".join(_element_list_en(analysis.avoid)) if analysis.avoid else "-"

    return {
        "summary": summary,
        "summary_en": (
            f"Day Master is {chart.day_master} ({_element_en(day_el)}), "
            f"born in the month of {_branch_en(chart.month.branch)}. "
            f"Pattern: {PATTERN_EN.get(analysis.pattern, analysis.pattern)}. "
            f"Favorable elements: {useful_en_str}. "
            f"Avoid: {avoid_en_str}."
        ),
        "personality": personality_zh,
        "personality_en": personality_en,
        "career": career_zh,
        "career_en": (
            f"Career prospects focus on the flow of Officer, Seal, and Eating/Injuring stars. "
            f"This chart forms a {PATTERN_EN.get(analysis.pattern, analysis.pattern)} pattern. "
            f"Favorable direction: cultivate {useful_en_str} energies. "
            f"Focus on professional expertise, rule-awareness, and consistent output."
        ),
        "wealth": wealth_zh,
        "wealth_en": (
            f"Wealth stars govern material resources and cash flow. "
            f"Favorable: {useful_en_str}. "
            f"Avoid: {avoid_en_str}. "
            f"Exercise caution with partnerships, lending, and high leverage if Wealth breaks Seal or Rob wealth conflicts."
        ),
        "relationships": _RELATIONSHIPS_ZH_TEMPLATE,
        "relationships_en": _RELATIONSHIPS_EN_TEMPLATE,
        "health": health_zh,
        "health_en": (
            f"Health follows elemental balance. "
            f"Nurture {useful_en_str} energies while moderating {avoid_en_str} influences. "
            f"Regular check-ups and a balanced lifestyle are always advisable."
        ),
        "advice": advice_zh,
        "advice_en": (
            f"Life advice: recognize the chart's inherent biases and use the luck cycles to rebalance. "
            f"Support {useful_en_str}, moderate {avoid_en_str}. "
            f"Let daily routines, diet, career choices, and relationships all align with elemental harmony."
        ),
    }


# ---------------------------------------------------------------------------
# Luck cycles transformation
# ---------------------------------------------------------------------------

_TONE_EN: dict[str, str] = {"吉": "auspicious", "慎": "cautious"}


def _build_luck_cycles(analysis: Any) -> list[dict[str, Any]]:
    """Transform analyzer luck_cycles into API format."""
    chart = analysis.chart
    today = date.today()
    current_age = today.year - chart.birth.birth_dt.year
    # Re-derive ages from the existing cycle entries to rebuild properly
    raw = analysis.luck_cycles
    result: list[dict[str, Any]] = []
    for idx, entry in enumerate(raw):
        ganzhi = entry["ganzhi"]
        # Parse ages from "6-15岁" format
        ages_str = entry.get("ages", "")
        age_start = 6 + idx * 10
        age_end = age_start + 9
        m = re.match(r"(\d+)-(\d+)", ages_str)
        if m:
            age_start = int(m.group(1))
            age_end = int(m.group(2))

        stem = ganzhi[0] if len(ganzhi) >= 1 else ""
        element = BRANCH_ELEMENT.get(ganzhi[1] if len(ganzhi) >= 2 else "", "")
        # Determine tone by checking if element is in useful list
        tone = "吉" if element in analysis.useful else "慎"

        result.append({
            "ganzhi": ganzhi,
            "ganzhi_en": _ganzhi_en(ganzhi),
            "age_start": age_start,
            "age_end": age_end,
            "element": element,
            "element_en": _element_en(element),
            "tone": _TONE_EN.get(tone, "cautious"),
            "current": age_start <= current_age <= age_end,
            "description": entry.get("detail", ""),
            "description_en": (
                f"{_ganzhi_en(ganzhi)} cycle — {_element_en(element)} energy enters the chart. "
                f"Observe career, finance, health and relationships per the chart's favorable/avoid guidelines."
            ),
        })
    return result


# ---------------------------------------------------------------------------
# LLM Enhancement
# ---------------------------------------------------------------------------

_LLM_SYSTEM_PROMPT = """你是一位精通中国传统八字命理学的资深命理师。你的任务是基于提供的八字排盘数据，生成专业、有实质内容的中英文命理分析。

请以 **纯净 JSON** 格式输出（不要包含 markdown 代码块标记或额外的说明文字），JSON 必须包含以下字段：

1. `summary` (string): 中文核心断语，概括命局最大特点（2-3句）
2. `summary_en` (string): 英文版核心断语
3. `personality` (string): 基于日主五行和命局组合的性格分析（中文，3-5句）
4. `personality_en` (string): 英文版性格分析
5. `career` (string): 事业发展方向和关键建议（中文，3-5句）
6. `career_en` (string): 英文版事业分析
7. `wealth` (string): 财富运势格局和理财建议（中文，3-5句）
8. `wealth_en` (string): 英文版财富分析
9. `relationships` (string): 感情婚姻特征和相处建议（中文，3-5句）
10. `relationships_en` (string): 英文版感情分析
11. `health` (string): 健康方面的五行提示（中文，2-3句）
12. `health_en` (string): 英文版健康提示
13. `advice` (string): 人生调适建议（中文，3-5句）
14. `advice_en` (string): 英文版人生建议
15. `luck_cycles_en` (array of objects): 每条大运的英文描述，每个对象包含 `{index: number, description_en: string}`

请确保分析内容专业、个性化、有实质信息，避免通用套话。必须基于提供的具体盘面数据进行分析。"""


async def _call_llm(analysis: Any, chart: Any) -> dict[str, Any] | None:
    """Call OpenAI-compatible API to generate enhanced analysis text.

    Returns a dict with section texts if successful, None otherwise.
    """
    api_key = os.environ.get("BAZI_API_KEY")
    if not api_key:
        return None

    api_base = os.environ.get("BAZI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("BAZI_API_MODEL", "gpt-4o")

    # Build the structured data from analysis
    pillar_data = {}
    for p in chart.pillars:
        pillar_data[p.name] = {
            "stem": p.stem,
            "branch": p.branch,
            "stem_en": _stem_en(p.stem),
            "branch_en": _branch_animal_en(p.branch),
            "element": STEM_ELEMENT[p.stem],
            "branch_element": BRANCH_ELEMENT[p.branch],
        }

    luck_data = []
    for idx, cycle in enumerate(analysis.luck_cycles):
        ganzhi = cycle["ganzhi"]
        luck_data.append({
            "index": idx,
            "ganzhi": ganzhi,
            "ganzhi_en": _ganzhi_en(ganzhi),
            "element": BRANCH_ELEMENT.get(ganzhi[1] if len(ganzhi) >= 2 else "", ""),
            "detail": cycle.get("detail", ""),
        })

    user_message = f"""## 命盘数据

- 八字：{chart.bazi} ({_bazi_en(chart.bazi)})
- 日主：{chart.day_master}（五行：{chart.day_element}）
- 性别：{chart.birth.gender}
- 出生时间：{chart.birth.birth_dt.isoformat(sep=" ")}

### 四柱
```json
{json.dumps(pillar_data, ensure_ascii=False, indent=2)}
```

### 五行分数
```json
{json.dumps(analysis.element_scores, ensure_ascii=False, indent=2)}
```

### 格局
- 格局：{analysis.pattern}
- 喜用：{', '.join(analysis.useful)}
- 忌神：{', '.join(analysis.avoid)}

### 大运
```json
{json.dumps(luck_data, ensure_ascii=False, indent=2)}
```

请根据以上命盘数据，严格按照要求的 JSON 格式输出命理分析。"""

    try:
        async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
            resp = await client.post(
                f"{api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            # Strip potential markdown code fences
            cleaned = content.strip()
            if cleaned.startswith("```"):
                # Remove opening fence (possibly with `json`)
                first_nl = cleaned.find("\n")
                if first_nl != -1:
                    cleaned = cleaned[first_nl + 1 :].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()
            result = json.loads(cleaned)
            logger.info("LLM analysis generated successfully (model=%s)", model)
            return result
    except httpx.HTTPStatusError as exc:
        logger.warning("LLM API HTTP error: %s - %s", exc.response.status_code, exc.response.text[:500])
    except httpx.RequestError as exc:
        logger.warning("LLM API request failed: %s", exc)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("LLM response parse failed: %s", exc)
    return None


def _merge_llm_sections(rule_sections: dict[str, str], llm_data: dict[str, Any], luck_cycles: list[dict[str, Any]]) -> dict[str, str]:
    """Merge LLM-generated section text into sections dict."""
    merged = dict(rule_sections)
    llm_fields = {
        "summary", "summary_en", "personality", "personality_en",
        "career", "career_en", "wealth", "wealth_en",
        "relationships", "relationships_en",
        "health", "health_en", "advice", "advice_en",
    }
    for field in llm_fields:
        val = llm_data.get(field)
        if val and isinstance(val, str):
            merged[field] = val

    # Merge luck cycle English descriptions
    luck_en_list = llm_data.get("luck_cycles_en", [])
    if luck_en_list and isinstance(luck_en_list, list):
        for item in luck_en_list:
            idx = item.get("index")
            desc = item.get("description_en", "")
            if idx is not None and isinstance(idx, int) and 0 <= idx < len(luck_cycles) and desc:
                luck_cycles[idx]["description_en"] = desc

    return merged


# ---------------------------------------------------------------------------
# Pydantic request model
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month")
    day: int = Field(..., ge=1, le=31, description="Birth day")
    hour: int | None = Field(None, ge=0, le=23, description="Birth hour (0-23), optional")
    minute: int = Field(0, ge=0, le=59, description="Birth minute")
    gender: str = Field(..., description="Gender: 'male' or 'female'")
    language: str = Field("zh", description="Preferred language: 'zh' or 'en'")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v.lower() not in ("male", "female"):
            raise ValueError("gender must be 'male' or 'female'")
        return v.lower()

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v.lower() not in ("zh", "en"):
            raise ValueError("language must be 'zh' or 'en'")
        return v.lower()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Bazi Mingyi API",
    description="八字命理分析 API — 整合排盘、规则分析与 LLM 增强",
    version="0.2.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning("Validation error: body=%s errors=%s", exc.body, exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static file serving (SPA frontend)
# ---------------------------------------------------------------------------

FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    logger.info("Serving static assets from %s", FRONTEND_DIST / "assets")
else:
    logger.info("No frontend/dist found at %s — API-only mode", FRONTEND_DIST)
    logger.info("No frontend/dist found at %s — API-only mode", FRONTEND_DIST)


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "0.2.0",
        "llm_enabled": bool(os.environ.get("BAZI_API_KEY")),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest) -> dict[str, Any]:
    """Accept structured birth data, compute bazi chart & analysis, optionally enhance with LLM."""
    try:
        # 1. Construct BirthInput directly (bypass text parser for structured input)
        gender_zh = GENDER_ZH.get(req.gender, "男")
        birth_hour = req.hour if req.hour is not None else 12
        birth_minute = req.minute if req.hour is not None else 0
        time_str = f"{req.hour:02d}:{req.minute:02d}" if req.hour is not None else "unknown time"
        raw_text = f"公历 {req.year} {req.month:02d} {req.day:02d} {time_str} {req.gender}"
        birth = BirthInput(
            raw_text=raw_text,
            calendar="solar",
            birth_dt=datetime(req.year, req.month, req.day, birth_hour, birth_minute),
            gender=gender_zh,
        )

        # 2. Build chart
        chart = build_chart(birth)

        # 3. Run rule-based analysis
        analysis = analyze_chart(chart)

        # 4. Build API response skeleton
        pillars_out = {}
        for p in chart.pillars:
            pillars_out[p.name] = {
                "stem": p.stem,
                "branch": p.branch,
                "stem_en": _stem_en(p.stem),
                "branch_en": _branch_animal_en(p.branch),
            }

        element_scores_cn = dict(analysis.element_scores)
        element_scores_en = {_element_en(k): v for k, v in analysis.element_scores.items()}

        luck_cycles = _build_luck_cycles(analysis)

        # 5. Build rule-based sections (fallback)
        rule_sections = _make_sections_rule(analysis, chart)

        # 6. Try LLM enhancement
        llm_enhanced = False
        if os.environ.get("BAZI_API_KEY"):
            llm_result = await _call_llm(analysis, chart)
            if llm_result is not None:
                rule_sections = _merge_llm_sections(rule_sections, llm_result, luck_cycles)
                llm_enhanced = True

        # 7. Assemble final response
        return {
            "bazi": chart.bazi,
            "bazi_en": _bazi_en(chart.bazi),
            "pillars": pillars_out,
            "day_master": chart.day_master,
            "day_element": chart.day_element,
            "day_element_en": _element_en(chart.day_element),
            "pattern": analysis.pattern,
            "pattern_en": PATTERN_EN.get(analysis.pattern, analysis.pattern),
            "element_scores": element_scores_cn,
            "element_scores_en": element_scores_en,
            "useful": list(analysis.useful),
            "useful_en": _element_list_en(analysis.useful),
            "avoid": list(analysis.avoid),
            "avoid_en": _element_list_en(analysis.avoid),
            "sections": rule_sections,
            "luck_cycles": luck_cycles,
            "llm_enhanced": llm_enhanced,
        }

    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc


# ---------------------------------------------------------------------------
# SPA catch-all — serve index.html for any non-API GET path
# ---------------------------------------------------------------------------

@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> HTMLResponse:
    if FRONTEND_DIST.is_dir():
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return HTMLResponse(index.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Not found")


# ---------------------------------------------------------------------------
# Entry point for direct execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("web.server:app", host="0.0.0.0", port=port, reload=True)
