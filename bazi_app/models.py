from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BirthInput:
    raw_text: str
    calendar: str
    birth_dt: datetime
    gender: str


@dataclass(frozen=True)
class Pillar:
    name: str
    stem: str
    branch: str

    @property
    def ganzhi(self) -> str:
        return f"{self.stem}{self.branch}"


@dataclass(frozen=True)
class Chart:
    birth: BirthInput
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    day_master: str
    day_element: str

    @property
    def pillars(self) -> list[Pillar]:
        return [self.year, self.month, self.day, self.hour]

    @property
    def bazi(self) -> str:
        return " ".join(p.ganzhi for p in self.pillars)


@dataclass(frozen=True)
class Analysis:
    chart: Chart
    element_scores: dict[str, float]
    pattern: str
    useful: list[str]
    avoid: list[str]
    relations: list[str]
    summary: str
    sections: dict[str, str]
    luck_cycles: list[dict[str, str]]
