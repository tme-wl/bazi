from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_chart
from .calendar import build_chart
from .parser import ParseError, parse_birth_text
from .prompt_builder import build_llm_prompt
from .renderer import write_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Bazi HTML report from one birth sentence.")
    parser.add_argument("text", help="一句包含公历生日、时间、性别的话，例如：我 公历 1991 07 06 am2点 男")
    parser.add_argument("-o", "--output", default="outputs/mingzhu.html", help="HTML 输出路径")
    parser.add_argument("--prompt-output", help="额外输出一份可发给 LLM 的完整 Markdown 提示词")
    args = parser.parse_args()

    try:
        birth = parse_birth_text(args.text)
    except ParseError as exc:
        raise SystemExit(f"解析失败：{exc}") from exc

    chart = build_chart(birth)
    analysis = analyze_chart(chart)
    output = write_html(analysis, Path(args.output))
    if args.prompt_output:
        prompt_path = Path(args.prompt_output)
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(build_llm_prompt(analysis), encoding="utf-8")
        print(f"提示词：{prompt_path.resolve()}")
    print(f"已生成：{output.resolve()}")
    print(f"八字：{chart.bazi}")
    print(f"总评：{analysis.summary}")


if __name__ == "__main__":
    main()
