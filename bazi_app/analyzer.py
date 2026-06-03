from __future__ import annotations

from datetime import date
from pathlib import Path

from .constants import (
    BRANCH_COMBOS,
    BRANCH_ELEMENT,
    CONTROLS,
    ELEMENTS,
    GENERATES,
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEMS,
    YANG_STEMS,
)
from .models import Analysis, Chart


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "bazi_mingyi.md"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def analyze_chart(chart: Chart, today: date | None = None) -> Analysis:
    today = today or date.today()
    scores = element_scores(chart)
    pattern = judge_pattern(chart, scores)
    useful, avoid = useful_and_avoid(chart.day_element, pattern)
    relations = relation_notes(chart)
    luck_cycles = build_luck_cycles(chart, today)
    sections = build_sections(chart, scores, pattern, useful, avoid, relations)
    summary = f"{chart.day_master}{chart.day_element}日主，生于{chart.month.branch}月，{pattern}。喜{''.join(useful)}，忌{''.join(avoid)}。"
    return Analysis(chart, scores, pattern, useful, avoid, relations, summary, sections, luck_cycles)


def element_scores(chart: Chart) -> dict[str, float]:
    scores = {element: 0.0 for element in ELEMENTS}
    for pillar in chart.pillars:
        scores[STEM_ELEMENT[pillar.stem]] += 1.0
        scores[BRANCH_ELEMENT[pillar.branch]] += 1.2
        for hidden in HIDDEN_STEMS[pillar.branch]:
            scores[STEM_ELEMENT[hidden]] += 0.35
    month_element = BRANCH_ELEMENT[chart.month.branch]
    scores[month_element] += 1.4
    return scores


def judge_pattern(chart: Chart, scores: dict[str, float]) -> str:
    day_element = chart.day_element
    support = scores[day_element] + scores[_generates_me(day_element)] * 0.75
    pressure = sum(value for element, value in scores.items() if element not in {day_element, _generates_me(day_element)})
    total = sum(scores.values())
    day_ratio = scores[day_element] / total
    if day_ratio > 0.42 and scores[_generates_me(day_element)] > 1.5:
        return "专旺格"
    if support < pressure * 0.35:
        return "从格"
    if support > pressure * 0.82:
        return "身强格"
    if support < pressure * 0.55:
        return "身弱格"
    return "平衡格"


def useful_and_avoid(day_element: str, pattern: str) -> tuple[list[str], list[str]]:
    if pattern in {"身强格", "专旺格"}:
        useful = [CONTROLS[day_element], GENERATES[day_element]]
        avoid = [day_element, _generates_me(day_element)]
    elif pattern == "从格":
        useful = [CONTROLS[day_element], GENERATES[CONTROLS[day_element]]]
        avoid = [day_element, _generates_me(day_element)]
    elif pattern == "身弱格":
        useful = [_generates_me(day_element), day_element]
        avoid = [CONTROLS[day_element], GENERATES[day_element]]
    else:
        useful = [_generates_me(day_element), CONTROLS[day_element]]
        avoid = [GENERATES[day_element]]
    return _unique(useful), _unique(avoid)


def relation_notes(chart: Chart) -> list[str]:
    notes: list[str] = []
    branches = [pillar.branch for pillar in chart.pillars]
    for relation, pairs in BRANCH_COMBOS.items():
        for left, right in pairs:
            if left in branches and right in branches:
                notes.append(f"{left}{right}{relation}")
    stems = [pillar.stem for pillar in chart.pillars]
    for stem in stems:
        element = STEM_ELEMENT[stem]
        if element == chart.day_element and stem != chart.day_master:
            notes.append(f"{stem}透天干，比劫助身")
        elif GENERATES[element] == chart.day_element:
            notes.append(f"{stem}为印星，生扶日主")
        elif CONTROLS[element] == chart.day_element:
            notes.append(f"{stem}为官杀，形成压力与约束")
        elif GENERATES[chart.day_element] == element:
            notes.append(f"{stem}为食伤，主表达才艺")
        elif CONTROLS[chart.day_element] == element:
            notes.append(f"{stem}为财星，主资源与财务")
    return _unique(notes) or ["命局关系较平，需重点看月令与大运流年触发。"]


def build_luck_cycles(chart: Chart, today: date) -> list[dict[str, str]]:
    forward = (chart.birth.gender == "男" and chart.year.stem in YANG_STEMS) or (
        chart.birth.gender == "女" and chart.year.stem not in YANG_STEMS
    )
    start_age = 6
    month_index = STEMS.index(chart.month.stem) % 10
    branch_order = "子丑寅卯辰巳午未申酉戌亥"
    branch_index = branch_order.index(chart.month.branch)
    cycles: list[dict[str, str]] = []
    current_age = today.year - chart.birth.birth_dt.year
    for idx in range(8):
        offset = idx + 1
        step = offset if forward else -offset
        stem = STEMS[(month_index + step) % 10]
        branch = branch_order[(branch_index + step) % 12]
        age_start = start_age + idx * 10
        age_end = age_start + 9
        element = STEM_ELEMENT[stem]
        tone = "吉" if element in useful_and_avoid(chart.day_element, judge_pattern(chart, element_scores(chart)))[0] else "慎"
        cycles.append(
            {
                "ganzhi": f"{stem}{branch}",
                "ages": f"{age_start}-{age_end}岁",
                "label": _cycle_label(tone, element),
                "current": "true" if age_start <= current_age <= age_end else "false",
                "detail": f"{stem}{branch}运，{element}气入局，宜按喜忌观察事业、财务、健康与关系起伏。",
            }
        )
    return cycles


def build_sections(
    chart: Chart,
    scores: dict[str, float],
    pattern: str,
    useful: list[str],
    avoid: list[str],
    relations: list[str],
) -> dict[str, str]:
    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)
    return {
        "pattern": f"此局以{chart.day_master}{chart.day_element}为日主，月令在{chart.month.branch}，五行以{strongest}气最显、{weakest}气较潜。综合月令、透干与藏干，判为{pattern}。取用以{''.join(useful)}为先，避{''.join(avoid)}太过。",
        "relations": "；".join(relations),
        "career": f"事业看官杀、印星与食伤的流通。此局{pattern}，宜取能承接{''.join(useful)}之气的方向，重视专业积累、规则意识与稳定输出。",
        "wealth": "财星主现实资源与现金流。若财星得用，则适合稳健经营；若财来破印或比劫争财，则合伙、借贷与高杠杆需谨慎。",
        "marriage": "日支为配偶宫，逢冲合刑害时关系议题容易被触发。相处宜少急躁、多沟通，重大决定避开情绪高点。",
        "health": _health_text(strongest, weakest, useful, avoid),
        "kinship": "年月为祖上父母，时柱为子女晚景。印比得力多得亲友助益，冲刑多时则各自独立、聚少离多之象较明显。",
        "advice": f"总论曰：命局贵在识其偏颇，再以行运调其失衡。此盘宜补{''.join(useful)}之象，少助{''.join(avoid)}之势；凡作息、饮食、职业节奏与人际选择，皆以平衡五行为要。",
    }


def _health_text(strongest: str, weakest: str, useful: list[str], avoid: list[str]) -> str:
    organs = {
        "木": "肝胆、筋目、情绪舒展",
        "火": "心血、睡眠、眼目与炎症",
        "土": "脾胃、代谢、肌肉与湿滞",
        "金": "肺皮毛、呼吸道与肃降",
        "水": "肾水、泌尿、腰膝与恢复力",
    }
    return f"健康以五行偏盛偏弱观其倾向：{strongest}旺则需防{organs[strongest]}太过，{weakest}弱则留意{organs[weakest]}不足。命理建议仅作传统文化参考，身体不适应以正规医疗检查为准。"


def _cycle_label(tone: str, element: str) -> str:
    if tone == "吉":
        return {"木": "生发", "火": "显达", "土": "稳基", "金": "收成", "水": "润局"}[element]
    return {"木": "慎执", "火": "慎躁", "土": "慎滞", "金": "慎刚", "水": "慎寒"}[element]


def _generates_me(element: str) -> str:
    for source, target in GENERATES.items():
        if target == element:
            return source
    raise KeyError(element)


def _unique(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
