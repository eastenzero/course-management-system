import os
import sys
import re
import csv
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = BASE_DIR / 'app' / 'backend'
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django

django.setup()

from django.db import models
from django.conf import settings
from apps.schedules.models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from django.contrib.auth import get_user_model

User = get_user_model()


def normalize_semester(sem: str) -> str:
    if not sem:
        return sem
    s = str(sem).strip()
    if re.fullmatch(r"\d{4}-\d{4}-(1|2)", s):
        return s
    m = re.fullmatch(r"(\d{4})-(1|2)", s)
    if m:
        y = int(m.group(1))
        term = m.group(2)
        return f"{y}-{y+1}-1" if term == '1' else f"{y-1}-{y}-2"
    s_no_space = re.sub(r"\s+", "", s)
    m2 = re.search(r"(\d{4}).*(春|秋)", s_no_space)
    if m2:
        y = int(m2.group(1))
        is_spring = (m2.group(2) == '春')
        return f"{y-1}-{y}-2" if is_spring else f"{y}-{y+1}-1"
    return s


def evaluate(semester: str):
    sem = normalize_semester(semester)
    total_courses = Course.objects.filter(semester=sem, is_active=True).count()
    scheduled_courses = Schedule.objects.filter(semester=sem, status='active').values('course').distinct().count()
    total_schedules = Schedule.objects.filter(semester=sem, status='active').count()
    total_classrooms = Classroom.objects.filter(is_active=True).count()
    used_classrooms = Schedule.objects.filter(semester=sem, status='active').values('classroom').distinct().count()
    coverage_rate = round((scheduled_courses / total_courses) * 100, 2) if total_courses else 0.0
    classroom_util = round((used_classrooms / total_classrooms) * 100, 2) if total_classrooms else 0.0

    day_dist = list(
        Schedule.objects.filter(semester=sem, status='active')
        .values('day_of_week')
        .annotate(count=models.Count('id'))
        .order_by('day_of_week')
    )
    weekend_count = sum(row['count'] for row in day_dist if row['day_of_week'] in [6, 7])

    ts_dist = list(
        Schedule.objects.filter(semester=sem, status='active')
        .values('time_slot__order', 'time_slot__name')
        .annotate(count=models.Count('id'))
        .order_by('time_slot__order')
    )

    teacher_workload = list(
        Schedule.objects.filter(semester=sem, status='active')
        .values('teacher__username')
        .annotate(schedule_count=models.Count('id'))
        .order_by('-schedule_count')
    )

    ts_ids = list({row['time_slot__order'] for row in ts_dist})
    cfg = getattr(settings, 'SCHEDULE_CONFIG', {})
    mint = cfg.get('two_hour_minutes_min', 115)
    maxt = cfg.get('two_hour_minutes_max', 125)
    used_ts = TimeSlot.objects.filter(schedules__semester=sem, schedules__status='active').distinct()
    two_hour_ok = used_ts.filter(duration_minutes__gte=mint, duration_minutes__lte=maxt).count()
    two_hour_total = used_ts.count()
    two_hour_ratio = round((two_hour_ok / two_hour_total) * 100, 2) if two_hour_total else 100.0

    summary = {
        'semester': sem,
        'total_courses': total_courses,
        'scheduled_courses': scheduled_courses,
        'coverage_rate_pct': coverage_rate,
        'total_schedules': total_schedules,
        'total_classrooms': total_classrooms,
        'used_classrooms': used_classrooms,
        'classroom_utilization_pct': classroom_util,
        'weekend_schedules': weekend_count,
        'two_hour_timeslot_ratio_pct': two_hour_ratio,
    }

    return summary, day_dist, ts_dist, teacher_workload


def write_csv(path: Path, rows, header=None):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if header:
            w.writerow(header)
        for r in rows:
            if isinstance(r, dict):
                if header:
                    w.writerow([r.get(h, '') for h in header])
                else:
                    w.writerow(list(r.values()))
            elif isinstance(r, (list, tuple)):
                w.writerow(r)
            else:
                w.writerow([r])


def write_markdown(path: Path, summary, day_dist, ts_dist, teacher_workload):
    lines = []
    lines.append(f"# 排课评估报告 ({summary['semester']})")
    lines.append("")
    lines.append("## 核心指标")
    for k, v in summary.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## 星期分布")
    for r in day_dist:
        lines.append(f"- **day {r['day_of_week']}**: {r['count']}")
    lines.append("")
    lines.append("## 时间段分布")
    for r in ts_dist:
        lines.append(f"- **order {r['time_slot__order']} {r['time_slot__name']}**: {r['count']}")
    lines.append("")
    lines.append("## 教师负载 Top")
    for r in teacher_workload[:20]:
        lines.append(f"- **{r['teacher__username']}**: {r['schedule_count']}")
    with path.open('w', encoding='utf-8') as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--semester', required=True)
    parser.add_argument('--prefix', default='eval')
    args = parser.parse_args()

    summary, day_dist, ts_dist, teacher_workload = evaluate(args.semester)

    out_dir = Path(__file__).resolve().parent
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = f"{args.prefix}_{summary['semester']}_{ts}"

    summary_csv = out_dir / f"{base}_summary.csv"
    day_csv = out_dir / f"{base}_days.csv"
    ts_csv = out_dir / f"{base}_timeslots.csv"
    teacher_csv = out_dir / f"{base}_teacher_workload.csv"
    md_path = out_dir / f"{base}_report.md"

    write_csv(summary_csv, [(k, v) for k, v in summary.items()], header=['metric', 'value'])
    write_csv(day_csv, day_dist, header=['day_of_week', 'count'])
    write_csv(ts_csv, ts_dist, header=['time_slot__order', 'time_slot__name', 'count'])
    write_csv(teacher_csv, teacher_workload, header=['teacher__username', 'schedule_count'])
    write_markdown(md_path, summary, day_dist, ts_dist, teacher_workload)

    print(str(summary_csv))
    print(str(day_csv))
    print(str(ts_csv))
    print(str(teacher_csv))
    print(str(md_path))


if __name__ == '__main__':
    main()
