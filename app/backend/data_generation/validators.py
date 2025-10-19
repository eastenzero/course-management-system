from typing import Dict, List, Tuple
from collections import defaultdict


def validate_and_summarize(dataset: Dict) -> Dict:
    counts = {
        "buildings": len(dataset.get("buildings", [])),
        "classrooms": len(dataset.get("classrooms", [])),
        "teachers": len(dataset.get("users", {}).get("teachers", [])),
        "courses": len(dataset.get("courses", [])),
        "time_slots": len(dataset.get("time_slots", [])),
        "schedules": len(dataset.get("schedules", [])),
    }

    # Indexes
    building_codes = {b["code"] for b in dataset.get("buildings", [])}
    classrooms = dataset.get("classrooms", [])
    classroom_index = {(c["building_code"], c["room_number"]): c for c in classrooms}
    teachers = {t["username"] for t in dataset.get("users", {}).get("teachers", [])}
    time_slot_orders = {ts["order"] for ts in dataset.get("time_slots", [])}
    courses = dataset.get("courses", [])
    course_index = {c["code"]: c for c in courses}

    # Violations counters
    teacher_conflicts = 0
    classroom_conflicts = 0
    capacity_violations = 0
    missing_refs = 0

    # Reference checks for courses
    for c in courses:
        # teachers exist
        for u in c.get("teacher_usernames", []) if c.get("teacher_usernames") else []:
            if u not in teachers:
                missing_refs += 1
        # min <= max
        if c.get("min_students", 0) > c.get("max_students", 0):
            capacity_violations += 1

    # Schedules checks
    seen_teacher = set()
    seen_room = set()
    for s in dataset.get("schedules", []):
        # refs
        cc = s.get("course_code")
        tu = s.get("teacher_username")
        bc = s.get("building_code")
        rn = s.get("room_number")
        tso = s.get("time_slot_order")
        dow = s.get("day_of_week")

        if cc not in course_index:
            missing_refs += 1
            continue
        if tu not in teachers:
            missing_refs += 1
        if (bc, rn) not in classroom_index:
            missing_refs += 1
        if tso not in time_slot_orders:
            missing_refs += 1
        if not isinstance(dow, int) or dow < 1 or dow > 7:
            missing_refs += 1

        # teacher in course.teachers
        course = course_index.get(cc)
        if course:
            if tu not in set(course.get("teacher_usernames", [])):
                missing_refs += 1

        # capacity
        room = classroom_index.get((bc, rn))
        if room and course:
            if int(room.get("capacity", 0)) < int(course.get("max_students", 0)):
                capacity_violations += 1

        # uniqueness for active in same semester
        if s.get("status", "active") == "active":
            key_t = (tu, s.get("semester"), dow, tso)
            key_r = (bc, rn, s.get("semester"), dow, tso)
            if key_t in seen_teacher:
                teacher_conflicts += 1
            else:
                seen_teacher.add(key_t)
            if key_r in seen_room:
                classroom_conflicts += 1
            else:
                seen_room.add(key_r)

    # Utilization estimate (by day): fraction of occupied (day, timeslot) pairs
    occupied_pairs = defaultdict(set)  # day -> set(time_slot_order)
    for s in dataset.get("schedules", []):
        if s.get("status", "active") != "active":
            continue
        occupied_pairs[s.get("day_of_week")].add(s.get("time_slot_order"))

    total_ts = len(time_slot_orders) if time_slot_orders else 1
    utilization_by_day: Dict[str, float] = {}
    for day, used in occupied_pairs.items():
        utilization_by_day[str(day)] = round(len(used) / total_ts, 4)

    # overall utilization as average over days encountered
    if utilization_by_day:
        overall = round(sum(utilization_by_day.values()) / len(utilization_by_day), 4)
    else:
        overall = 0.0

    summary = {
        "counts": counts,
        "violations": {
            "teacher_timeslot_conflicts": teacher_conflicts,
            "classroom_timeslot_conflicts": classroom_conflicts,
            "capacity_violations": capacity_violations,
            "missing_refs": missing_refs,
        },
        "utilization": {
            "by_day": utilization_by_day,
            "overall": overall,
        },
    }

    dataset["summary"] = summary
    return dataset
