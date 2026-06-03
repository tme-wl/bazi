from __future__ import annotations

from datetime import datetime

from .constants import (
    BRANCHES,
    GANZHI,
    HOUR_BRANCH_BY_HOUR,
    HOUR_STEM_START_BY_DAY_STEM,
    MONTH_BRANCHES,
    MONTH_STEM_START_BY_YEAR_STEM,
    STEMS,
    STEM_ELEMENT,
)
from .models import BirthInput, Chart, Pillar


SOLAR_TERM_STARTS = [
    (2, 4, "寅"),
    (3, 6, "卯"),
    (4, 5, "辰"),
    (5, 6, "巳"),
    (6, 6, "午"),
    (7, 7, "未"),
    (8, 8, "申"),
    (9, 8, "酉"),
    (10, 8, "戌"),
    (11, 7, "亥"),
    (12, 7, "子"),
    (1, 6, "丑"),
]


def build_chart(birth: BirthInput) -> Chart:
    dt = birth.birth_dt
    year_pillar = _year_pillar(dt)
    month_pillar = _month_pillar(dt, year_pillar.stem)
    day_pillar = _day_pillar(dt)
    hour_pillar = _hour_pillar(dt, day_pillar.stem)
    return Chart(
        birth=birth,
        year=year_pillar,
        month=month_pillar,
        day=day_pillar,
        hour=hour_pillar,
        day_master=day_pillar.stem,
        day_element=STEM_ELEMENT[day_pillar.stem],
    )


def _year_pillar(dt: datetime) -> Pillar:
    year = dt.year
    if (dt.month, dt.day) < (2, 4):
        year -= 1
    index = (year - 1984) % 60
    return _pillar("年柱", index)


def _month_pillar(dt: datetime, year_stem: str) -> Pillar:
    branch = _month_branch(dt)
    branch_index = MONTH_BRANCHES.index(branch)
    start_stem = MONTH_STEM_START_BY_YEAR_STEM[year_stem]
    stem = STEMS[(STEMS.index(start_stem) + branch_index) % 10]
    return Pillar("月柱", stem, branch)


def _month_branch(dt: datetime) -> str:
    candidates: list[tuple[datetime, str]] = []
    for month, day, branch in SOLAR_TERM_STARTS:
        year = dt.year
        if month == 1 and dt.month != 1:
            year += 1
        if month in (11, 12) and dt.month == 1:
            year -= 1
        candidates.append((datetime(year, month, day), branch))
    candidates.sort(key=lambda item: item[0])
    current = candidates[0][1]
    for start, branch in candidates:
        if dt >= start:
            current = branch
        else:
            break
    return current


def _day_pillar(dt: datetime) -> Pillar:
    index = (_julian_day_number(dt.year, dt.month, dt.day) + 59) % 60
    return _pillar("日柱", index)


def _hour_pillar(dt: datetime, day_stem: str) -> Pillar:
    branch = _hour_branch(dt.hour)
    branch_index = BRANCHES.index(branch)
    start_stem = HOUR_STEM_START_BY_DAY_STEM[day_stem]
    stem = STEMS[(STEMS.index(start_stem) + branch_index) % 10]
    return Pillar("时柱", stem, branch)


def _hour_branch(hour: int) -> str:
    if hour == 23:
        return "子"
    for start, branch in reversed(HOUR_BRANCH_BY_HOUR[1:]):
        if hour >= start:
            return branch
    return "子"


def _pillar(name: str, index: int) -> Pillar:
    gz = GANZHI[index]
    return Pillar(name, gz[0], gz[1])


def _julian_day_number(year: int, month: int, day: int) -> int:
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
