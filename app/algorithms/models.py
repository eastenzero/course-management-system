from dataclasses import dataclass


@dataclass
class Assignment:
    course_id: int
    teacher_id: int
    classroom_id: int
    day_of_week: int  # 1..7
    time_slot: int    # 1..20 (order)
    semester: str = "2024春"
    academic_year: str = "2023-2024"
    week_range: str = "1-16"


@dataclass
class TeacherPreference:
    teacher_id: int
    day_of_week: int
    time_slot: int
    preference_score: float
    is_available: bool
    reason: str = ""
