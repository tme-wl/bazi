from __future__ import annotations

import re
from datetime import datetime

from .models import BirthInput


class ParseError(ValueError):
    pass


def parse_birth_text(text: str) -> BirthInput:
    normalized = _normalize(text)
    calendar = "solar"
    if "农历" in normalized or "阴历" in normalized:
        raise ParseError("当前版本只支持公历输入，请提供公历年月日时。")

    gender = _parse_gender(normalized)
    year, month, day = _parse_date(normalized)
    hour, minute = _parse_time(normalized)
    return BirthInput(
        raw_text=text,
        calendar=calendar,
        birth_dt=datetime(year, month, day, hour, minute),
        gender=gender,
    )


def _normalize(text: str) -> str:
    table = str.maketrans("０１２３４５６７８９：，。；（）", "0123456789:,.;()")
    return text.translate(table).lower().replace("凌晨", "am").replace("上午", "am").replace("下午", "pm").replace("晚上", "pm")


def _parse_gender(text: str) -> str:
    if re.search(r"男|male|man|m\b", text):
        return "男"
    if re.search(r"女|female|woman|f\b", text):
        return "女"
    raise ParseError("没有识别到性别，请在输入中包含“男”或“女”。")


def _parse_date(text: str) -> tuple[int, int, int]:
    patterns = [
        r"(?P<y>19\d{2}|20\d{2})\D+(?P<m>\d{1,2})\D+(?P<d>\d{1,2})",
        r"(?P<y>19\d{2}|20\d{2})(?P<m>\d{2})(?P<d>\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match["y"]), int(match["m"]), int(match["d"])
    raise ParseError("没有识别到公历日期，请使用类似“公历 1991 07 06”的格式。")


def _parse_time(text: str) -> tuple[int, int]:
    minute = 0
    ampm = None
    match = re.search(r"\b(am|pm)\s*(\d{1,2})(?:[:点时](\d{1,2}))?", text)
    if match:
        ampm = match.group(1)
        hour = int(match.group(2))
        if match.group(3):
            minute = int(match.group(3))
    else:
        match = re.search(r"(\d{1,2})(?:[:点时](\d{1,2}))?\s*(?:分)?", _strip_date(text))
        if not match:
            raise ParseError("没有识别到出生时间，请使用类似“am2点”或“02:00”的格式。")
        hour = int(match.group(1))
        if match.group(2):
            minute = int(match.group(2))

    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        raise ParseError("出生时间超出有效范围。")
    return hour, minute


def _strip_date(text: str) -> str:
    return re.sub(r"(19\d{2}|20\d{2})\D+\d{1,2}\D+\d{1,2}", " ", text)
