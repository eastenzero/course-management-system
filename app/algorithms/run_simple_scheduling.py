from typing import List, Dict, Tuple
try:
    from .models import Assignment, TeacherPreference
except Exception:
    # Fallback when imported as a top-level module (no package context)
    from models import Assignment, TeacherPreference


def create_simple_test_data() -> Tuple[List[Dict], List[Dict], List[Dict], List[TeacherPreference]]:
    courses = [
        {"id": i, "name": f"课程{i}", "code": f"C{i:03d}", "credits": 2, "max_students": 60,
         "course_type": "required", "semester": "2024春", "academic_year": "2023-2024",
         "is_active": True, "is_published": True}
        for i in range(1, 6)
    ]
    teachers = [
        {"id": i, "name": f"教师{i}", "department": "计算机学院",
         "max_weekly_hours": 16, "max_daily_hours": 6, "qualified_courses": [c["id"] for c in courses],
         "title": "lecturer"}
        for i in range(1, 4)
    ]
    classrooms = [
        {"id": i, "name": f"教学楼A{i:03d}", "building": "A", "floor": 1, "capacity": 100,
         "room_type": "lecture", "equipment": [], "is_available": True, "is_active": True}
        for i in range(101, 106)
    ]
    prefs = []
    for t in teachers:
        # 两个偏好
        prefs.append(TeacherPreference(teacher_id=t["id"], day_of_week=1, time_slot=2, preference_score=0.9, is_available=True, reason="偏好上午"))
        prefs.append(TeacherPreference(teacher_id=t["id"], day_of_week=3, time_slot=3, preference_score=0.8, is_available=True, reason="偏好中段"))
    return courses, teachers, classrooms, prefs


def run_simple_scheduling() -> Dict:
    courses, teachers, classrooms, prefs = create_simple_test_data()

    assignments: List[Dict] = []
    used_teacher_slots = set()  # (teacher_id, day, ts)
    used_room_slots = set()     # (room_id, day, ts)

    # 简单贪心：按课程循环，优先使用偏好槽
    days = [1, 2, 3, 4, 5]
    time_slots = [1, 2, 3, 4, 5, 6, 7, 8]

    teacher_ids = [t["id"] for t in teachers]
    room_ids = [c["id"] for c in classrooms]

    for idx, c in enumerate(courses):
        assigned = False
        # 选教师（轮询）
        teacher_id = teacher_ids[idx % len(teacher_ids)]

        # 先按偏好尝试
        preferred = [p for p in prefs if p.teacher_id == teacher_id]
        for p in preferred:
            for room_id in room_ids:
                key_t = (teacher_id, p.day_of_week, p.time_slot)
                key_r = (room_id, p.day_of_week, p.time_slot)
                if key_t in used_teacher_slots or key_r in used_room_slots:
                    continue
                assignments.append({
                    "course_id": c["id"],
                    "teacher_id": teacher_id,
                    "classroom_id": room_id,
                    "day_of_week": p.day_of_week,
                    "time_slot": p.time_slot,
                    "semester": c["semester"],
                    "academic_year": c["academic_year"],
                    "week_range": "1-16",
                })
                used_teacher_slots.add(key_t)
                used_room_slots.add(key_r)
                assigned = True
                break
            if assigned:
                break
        # 再尝试任意可用槽
        if not assigned:
            for d in days:
                for ts in time_slots:
                    for room_id in room_ids:
                        key_t = (teacher_id, d, ts)
                        key_r = (room_id, d, ts)
                        if key_t in used_teacher_slots or key_r in used_room_slots:
                            continue
                        assignments.append({
                            "course_id": c["id"],
                            "teacher_id": teacher_id,
                            "classroom_id": room_id,
                            "day_of_week": d,
                            "time_slot": ts,
                            "semester": c["semester"],
                            "academic_year": c["academic_year"],
                            "week_range": "1-16",
                        })
                        used_teacher_slots.add(key_t)
                        used_room_slots.add(key_r)
                        assigned = True
                        break
                    if assigned:
                        break
                if assigned:
                    break

    success_rate = round(len(assignments) / len(courses) * 100 if courses else 0, 1)
    return {
        "algorithm": "simple",
        "success_rate": success_rate,
        "assignments": assignments,
    }
