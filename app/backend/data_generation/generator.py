import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
try:
    from .params import GenerationParams
except Exception:
    # Fallback for running as a script (no package context)
    from params import GenerationParams


class DataGenerator:
    def __init__(self, params: GenerationParams):
        self.p = params
        self.rng = random.Random(params.seed)
        self.depts: List[Tuple[str, str]] = [
            ("计算机学院", "CS"),
            ("软件学院", "SE"),
            ("信息工程学院", "IE"),
            ("数学与统计学院", "MATH"),
            ("物理与电子工程学院", "PHY"),
            ("经济与管理学院", "ECON"),
        ]
        self.room_types = [
            "lecture",
            "lab",
            "computer",
            "multimedia",
            "seminar",
            "auditorium",
            "studio",
            "library",
            "gym",
            "other",
        ]
        self.course_types = [
            "required",
            "elective",
            "public",
            "professional",
        ]

    def _time_slots(self) -> List[Dict]:
        n = max(1, int(self.p.timeslots_per_day))
        base = datetime(2000, 1, 1, 8, 0)
        slots = []
        t = base
        for i in range(1, n + 1):
            start = t
            end = start + timedelta(minutes=45)
            slots.append(
                {
                    "name": f"第{i}节",
                    "start_time": start.strftime("%H:%M"),
                    "end_time": end.strftime("%H:%M"),
                    "order": i,
                    "duration_minutes": 45,
                }
            )
            t = end + timedelta(minutes=10)
        return slots

    def _buildings(self) -> List[Dict]:
        count = max(1, int(self.p.num_buildings))
        codes = []
        for i in range(count):
            codes.append(chr(ord("A") + i))
        buildings = []
        for c in codes:
            buildings.append({"code": c, "name": f"{c}号教学楼", "address": "校区"})
        return buildings

    def _classrooms(self, buildings: List[Dict]) -> List[Dict]:
        total = max(1, int(self.p.num_classrooms))
        per = total // max(1, len(buildings))
        rem = total - per * len(buildings)
        rooms: List[Dict] = []
        used: set = set()
        idx = 0
        for b in buildings:
            cnt = per + (1 if idx < rem else 0)
            idx += 1
            for _ in range(cnt):
                floor = self.rng.randint(1, 6)
                num = self.rng.randint(1, 30)
                room_number = f"{floor:01d}{num:02d}"
                key = (b["code"], room_number)
                while key in used:
                    floor = self.rng.randint(1, 6)
                    num = self.rng.randint(1, 30)
                    room_number = f"{floor:01d}{num:02d}"
                    key = (b["code"], room_number)
                used.add(key)
                room_type = self.rng.choice(self.room_types)
                capacity = self._capacity_for_room_type(room_type)
                equip = {
                    "projector": room_type in {"lecture", "multimedia", "auditorium", "seminar"},
                    "ac": True,
                    "computer": room_type in {"computer", "lab"},
                }
                rooms.append(
                    {
                        "building_code": b["code"],
                        "room_number": room_number,
                        "name": f"{b['code']}{room_number}",
                        "capacity": capacity,
                        "room_type": room_type,
                        "floor": int(room_number[0]),
                        "equipment": equip,
                        "is_available": True,
                        "is_active": True,
                    }
                )
        return rooms

    def _capacity_for_room_type(self, room_type: str) -> int:
        if room_type == "lecture":
            return self.rng.randint(60, 150)
        if room_type == "lab":
            return self.rng.randint(30, 60)
        if room_type == "computer":
            return self.rng.randint(40, 100)
        if room_type == "multimedia":
            return self.rng.randint(60, 120)
        if room_type == "auditorium":
            return self.rng.randint(120, 240)
        if room_type == "seminar":
            return self.rng.randint(30, 50)
        if room_type == "library":
            return self.rng.randint(50, 120)
        if room_type == "gym":
            return self.rng.randint(80, 200)
        if room_type == "studio":
            return self.rng.randint(20, 40)
        return self.rng.randint(30, 120)

    def _teachers(self) -> List[Dict]:
        n = max(1, int(self.p.num_teachers))
        teachers = []
        for i in range(1, n + 1):
            dept = self.rng.choice(self.depts)[0]
            username = f"t_{i:03d}"
            teachers.append(
                {
                    "username": username,
                    "employee_id": f"T{i:04d}",
                    "department": dept,
                }
            )
        return teachers

    def _courses(self, teachers: List[Dict]) -> List[Dict]:
        n = max(1, int(self.p.num_courses))
        teacher_usernames = [t["username"] for t in teachers]
        courses = []
        for i in range(1, n + 1):
            dept_name, prefix = self.rng.choice(self.depts)
            code = f"{prefix}{100 + (i % 900)}"
            name = f"课程{i:03d}"
            english_name = None
            credits = self.rng.randint(1, 10)
            hours = self.rng.choice([16, 32, 48, 64, 80, 96, 128, 160, 192, 200])
            course_type = self.rng.choice(self.course_types)
            max_students = self.rng.choice([30, 50, 80, 100, 120])
            min_students = self.rng.randint(10, min(30, max_students))
            k = self.rng.randint(1, min(3, len(teacher_usernames)))
            assigned = self.rng.sample(teacher_usernames, k)
            courses.append(
                {
                    "code": code,
                    "name": name,
                    "english_name": english_name,
                    "credits": credits,
                    "hours": hours,
                    "course_type": course_type,
                    "department": dept_name,
                    "semester": self.p.semester,
                    "academic_year": self.p.academic_year,
                    "teacher_usernames": assigned,
                    "max_students": max_students,
                    "min_students": min_students,
                }
            )
        return courses

    def _days(self) -> List[int]:
        days = min(7, max(1, int(self.p.days_per_week)))
        if not self.p.include_weekend:
            days = min(days, 5)
        return list(range(1, days + 1))

    def _choose_room_for_course(self, classrooms: List[Dict], needed: int) -> Dict:
        candidates = [c for c in classrooms if c["capacity"] >= needed]
        if not candidates:
            candidates = sorted(classrooms, key=lambda x: x["capacity"])[:1]
        return self.rng.choice(candidates)

    def _schedules(self, courses: List[Dict], classrooms: List[Dict], time_slots: List[Dict]) -> List[Dict]:
        days = self._days()
        schedules: List[Dict] = []
        busy_teacher = set()
        busy_room = set()
        for course in courses:
            teacher = self.rng.choice(course["teacher_usernames"]) if course["teacher_usernames"] else None
            if not teacher:
                continue
            allocated = False
            for _ in range(2000):
                ts = self.rng.choice(time_slots)
                day = self.rng.choice(days)
                room = self._choose_room_for_course(classrooms, course["max_students"])
                key_t = (teacher, day, ts["order"])
                key_r = (room["building_code"], room["room_number"], day, ts["order"])
                if key_t in busy_teacher or key_r in busy_room:
                    continue
                busy_teacher.add(key_t)
                busy_room.add(key_r)
                schedules.append(
                    {
                        "course_code": course["code"],
                        "teacher_username": teacher,
                        "building_code": room["building_code"],
                        "room_number": room["room_number"],
                        "time_slot_order": ts["order"],
                        "day_of_week": day,
                        "week_range": f"1-{self.p.weeks_total}周",
                        "semester": self.p.semester,
                        "academic_year": self.p.academic_year,
                        "status": "active",
                    }
                )
                allocated = True
                break
            if not allocated:
                pass
        if self.p.conflict_rate and self.p.conflict_rate > 0:
            self._inject_conflicts(schedules, time_slots)
        return schedules

    def _inject_conflicts(self, schedules: List[Dict], time_slots: List[Dict]) -> None:
        k = int(len(schedules) * float(self.p.conflict_rate))
        if k <= 0:
            return
        days = self._days()
        for _ in range(k):
            if not schedules:
                break
            base = self.rng.choice(schedules)
            conflict_type = self.rng.choice(["teacher", "classroom"])
            if conflict_type == "teacher":
                ts = base["time_slot_order"]
                day = base["day_of_week"]
                schedules.append(
                    {
                        "course_code": base["course_code"],
                        "teacher_username": base["teacher_username"],
                        "building_code": base["building_code"],
                        "room_number": base["room_number"],
                        "time_slot_order": ts,
                        "day_of_week": day,
                        "week_range": base["week_range"],
                        "semester": base["semester"],
                        "academic_year": base["academic_year"],
                        "status": "active",
                    }
                )
            else:
                ts = base["time_slot_order"]
                day = base["day_of_week"]
                schedules.append(
                    {
                        "course_code": base["course_code"],
                        "teacher_username": base["teacher_username"],
                        "building_code": base["building_code"],
                        "room_number": base["room_number"],
                        "time_slot_order": ts,
                        "day_of_week": day,
                        "week_range": base["week_range"],
                        "semester": base["semester"],
                        "academic_year": base["academic_year"],
                        "status": "active",
                    }
                )

    def generate(self) -> Dict:
        buildings = self._buildings()
        classrooms = self._classrooms(buildings)
        teachers = self._teachers()
        users = {"teachers": teachers, "students": []}
        time_slots = self._time_slots()
        courses = self._courses(teachers)
        schedules = self._schedules(courses, classrooms, time_slots)
        dataset = {
            "seed": self.p.seed,
            "semester": self.p.semester,
            "academic_year": self.p.academic_year,
            "buildings": buildings,
            "classrooms": classrooms,
            "users": users,
            "courses": courses,
            "time_slots": time_slots,
            "schedules": schedules,
        }
        return dataset
