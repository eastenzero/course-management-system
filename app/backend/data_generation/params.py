from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationParams:
    seed: Optional[int] = None
    semester: str = "2024-2025-1"
    academic_year: str = "2024-2025"
    num_buildings: int = 3
    num_classrooms: int = 40
    num_teachers: int = 40
    num_courses: int = 120
    days_per_week: int = 5
    timeslots_per_day: int = 8
    weeks_total: int = 16
    utilization_level: str = "medium"
    conflict_rate: float = 0.0
    include_weekend: bool = False
    output: Optional[str] = None
