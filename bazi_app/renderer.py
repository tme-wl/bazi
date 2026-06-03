from __future__ import annotations

import html
from pathlib import Path

from .analyzer import load_prompt
from .constants import ELEMENTS
from .models import Analysis


ELEMENT_ICONS = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}
ELEMENT_COLORS = {"木": "#4a7c59", "火": "#c94040", "土": "#b8860b", "金": "#c0c0c0", "水": "#3a6ea8"}


def render_html(analysis: Analysis) -> str:
    chart = analysis.chart
    max_score = max(analysis.element_scores.values()) or 1
    prompt_note = html.escape(load_prompt().splitlines()[1] if load_prompt() else "bazi-mingyi")
    bars = "\n".join(
        _element_bar(element, analysis.element_scores[element], max_score)
        for element in ELEMENTS
    )
    pillars = "\n".join(
        f"""
        <div class="pillar">
          <div class="pillar-name">{html.escape(pillar.name)}</div>
          <div class="stem">{pillar.stem}</div>
          <div class="branch">{pillar.branch}</div>
        </div>
        """
        for pillar in chart.pillars
    )
    relations = "".join(f"<li>{html.escape(item)}</li>" for item in analysis.relations)
    luck = "".join(_luck_node(item) for item in analysis.luck_cycles)
    useful = "".join(f"<span>{item}</span>" for item in analysis.useful)
    avoid = "".join(f"<span>{item}</span>" for item in analysis.avoid)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>命书 - {html.escape(chart.bazi)}</title>
  <style>
    :root {{
      --bg-primary:#0d0d0e; --bg-surface:#141416; --bg-elevated:#1c1c1f;
      --border-subtle:#2a2a2f; --gold-bright:#d4a853; --gold-muted:#8a6f3a;
      --vermillion:#c94040; --vermillion-soft:#8b2e2e; --text-primary:#e8e4dc;
      --text-secondary:#9b9590; --text-muted:#5a5753; --jade:#4a8b6f;
    }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{
      margin:0; background:radial-gradient(circle at 15% 10%, rgba(212,168,83,.12), transparent 24rem), var(--bg-primary);
      color:var(--text-primary); font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      line-height:1.75;
    }}
    main {{ max-width:1120px; margin:0 auto; padding:40px 20px 80px; }}
    .hero {{
      min-height:62vh; display:grid; align-items:center; border-bottom:1px solid rgba(212,168,83,.28);
      background-image: radial-gradient(circle, rgba(212,168,83,.08) 1px, transparent 1px);
      background-size: 22px 22px;
    }}
    .title {{ font-family:serif; font-size:clamp(48px, 9vw, 112px); letter-spacing:.65em; color:var(--gold-bright); margin:0; }}
    .subtitle {{ color:var(--text-secondary); letter-spacing:.2em; text-transform:uppercase; }}
    .pillars {{ display:grid; grid-template-columns:repeat(4, minmax(120px, 1fr)); gap:1px; margin-top:36px; background:var(--border-subtle); }}
    .pillar {{ background:rgba(20,20,22,.94); text-align:center; padding:24px 12px; }}
    .pillar-name {{ color:var(--text-muted); font-size:13px; letter-spacing:.24em; }}
    .stem {{ color:var(--gold-bright); font-size:54px; font-family:serif; line-height:1.15; }}
    .branch {{ color:var(--vermillion); font-size:48px; font-family:serif; line-height:1.15; }}
    section {{ padding:44px 0; animation:fadeInUp .7s ease both; }}
    h2 {{ color:var(--gold-bright); font-family:serif; letter-spacing:.18em; font-size:28px; margin:0 0 18px; }}
    .lead {{ font-size:20px; color:var(--text-primary); }}
    .tag {{ display:inline-flex; border:1px solid var(--gold-muted); color:var(--gold-bright); padding:6px 12px; border-radius:999px; margin-right:8px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr)); gap:16px; }}
    .card {{ background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:8px; padding:20px; }}
    .card h3 {{ margin:0 0 10px; color:var(--gold-bright); font-size:18px; }}
    .bar-row {{ display:grid; grid-template-columns:64px 1fr 64px; gap:12px; align-items:center; margin:14px 0; }}
    .bar-track {{ height:12px; background:var(--bg-elevated); border-radius:999px; overflow:hidden; }}
    .bar-fill {{ height:100%; width:var(--w); background:var(--c); border-radius:999px; animation:grow 1.1s ease both; }}
    .badges span {{ display:inline-block; margin:6px 8px 6px 0; padding:8px 14px; border-radius:999px; }}
    .good span {{ background:rgba(74,139,111,.18); color:#8fd1b6; border:1px solid rgba(74,139,111,.6); }}
    .bad span {{ background:rgba(201,64,64,.16); color:#f0a0a0; border:1px solid rgba(201,64,64,.58); }}
    .timeline {{ display:flex; gap:18px; overflow-x:auto; padding:20px 4px 30px; }}
    .node {{ min-width:138px; border:1px solid var(--border-subtle); border-top:3px solid var(--gold-muted); background:var(--bg-surface); border-radius:8px; padding:16px; }}
    .node.current {{ border-top-color:var(--gold-bright); box-shadow:0 0 0 3px rgba(212,168,83,.08); }}
    .node strong {{ display:block; color:var(--gold-bright); font-size:22px; }}
    ul {{ padding-left:20px; }}
    .meta {{ color:var(--text-secondary); }}
    footer {{ color:var(--text-muted); border-top:1px solid var(--border-subtle); padding-top:24px; font-size:13px; }}
    @keyframes fadeInUp {{ from {{ opacity:0; transform:translateY(18px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @keyframes grow {{ from {{ width:0; }} to {{ width:var(--w); }} }}
    @media (max-width: 720px) {{
      .pillars {{ grid-template-columns:repeat(2, 1fr); }}
      .title {{ letter-spacing:.38em; }}
      .bar-row {{ grid-template-columns:48px 1fr 52px; }}
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <div>
      <p class="subtitle">Bazi Mingyi</p>
      <h1 class="title">命书</h1>
      <p class="meta">公历 {chart.birth.birth_dt:%Y-%m-%d %H:%M} ｜ {chart.birth.gender} ｜ {html.escape(chart.bazi)}</p>
      <div class="pillars">{pillars}</div>
    </div>
  </section>

  <section>
    <h2>格局总评</h2>
    <p class="lead">{html.escape(analysis.summary)}</p>
    <span class="tag">{html.escape(analysis.pattern)}</span>
    <span class="tag">日主 {chart.day_master}{chart.day_element}</span>
    <p>{html.escape(analysis.sections["pattern"])}</p>
  </section>

  <section>
    <h2>五行能量图</h2>
    <div class="card">{bars}</div>
  </section>

  <section>
    <h2>关系网络</h2>
    <div class="grid">
      <div class="card"><h3>关系列表</h3><ul>{relations}</ul></div>
      <div class="card"><h3>结构说明</h3><p>{html.escape(analysis.sections["relations"])}</p></div>
    </div>
  </section>

  <section>
    <h2>喜用忌神</h2>
    <div class="grid">
      <div class="card"><h3>喜用</h3><div class="badges good">{useful}</div></div>
      <div class="card"><h3>忌神</h3><div class="badges bad">{avoid}</div></div>
    </div>
  </section>

  <section>
    <h2>六亲人事</h2>
    <div class="grid">
      <div class="card"><h3>事业</h3><p>{html.escape(analysis.sections["career"])}</p></div>
      <div class="card"><h3>财运</h3><p>{html.escape(analysis.sections["wealth"])}</p></div>
      <div class="card"><h3>婚姻</h3><p>{html.escape(analysis.sections["marriage"])}</p></div>
      <div class="card"><h3>健康</h3><p>{html.escape(analysis.sections["health"])}</p></div>
      <div class="card"><h3>六亲</h3><p>{html.escape(analysis.sections["kinship"])}</p></div>
    </div>
  </section>

  <section>
    <h2>大运流年</h2>
    <div class="timeline">{luck}</div>
  </section>

  <section>
    <h2>总论与调适</h2>
    <p>{html.escape(analysis.sections["advice"])}</p>
  </section>

  <footer>
    <p>本命书由本地 Python 项目生成，规则提示词来自 prompts/bazi_mingyi.md。{prompt_note}</p>
    <p>命理内容仅作传统文化参考，不构成医疗、法律或投资建议。</p>
  </footer>
</main>
</body>
</html>
"""


def write_html(analysis: Analysis, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(analysis), encoding="utf-8")
    return output_path


def _element_bar(element: str, score: float, max_score: float) -> str:
    width = max(6, round(score / max_score * 100, 1))
    return f"""
      <div class="bar-row">
        <div>{ELEMENT_ICONS[element]} {element}</div>
        <div class="bar-track"><div class="bar-fill" style="--w:{width}%; --c:{ELEMENT_COLORS[element]}"></div></div>
        <div>{score:.1f}</div>
      </div>
    """


def _luck_node(item: dict[str, str]) -> str:
    current = " current" if item.get("current") == "true" else ""
    return f"""
      <div class="node{current}" title="{html.escape(item["detail"])}">
        <strong>{html.escape(item["ganzhi"])}</strong>
        <span>{html.escape(item["ages"])}</span>
        <p>{html.escape(item["label"])}</p>
      </div>
    """
