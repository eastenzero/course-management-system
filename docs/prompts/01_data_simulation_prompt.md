# 提示词：大学排课系统数据模拟（Buildings/Classrooms/Users/Courses/TimeSlots/Enrollments）

- 目标
  - 为学期（semester）`{{SEMESTER}}` 和学年（academic_year）`{{ACADEMIC_YEAR}}` 批量生成可用于排课算法与前端演示的模拟数据。
  - 所有字段严格遵守当前模型约束，便于通过管理命令或 ORM 写入数据库。

- 上下文（模型与关键字段）
  - 课程 `Course`（`apps/courses/models.py`）
    - 唯一：`code`
    - 字段：`name`、`credits[1..10]`、`hours[1..200]`（总学时，18周）、`course_type∈{required,elective,public,professional}`、`department`、`semester`（如`2024-2025-1`）、`academic_year`（如`2024-2025`）、`is_active`、`is_published`
    - 关系：`teachers(M2M: User where user_type=teacher)`、`prerequisites(M2M: Course)`
    - 选课人数：`max_students(>=min_students)`、`min_students`
  - 教室 `Classroom`（`apps/classrooms/models.py`）
    - 归属：`building(FK)`；唯一：`(building, room_number)`
    - 字段：`capacity`、`room_type∈{lecture,lab,computer,...}`、`floor`、`equipment(JSON)`、`is_available`、`is_active`
  - 时间段 `TimeSlot`（`apps/schedules/models.py`）
    - 字段：`name`、`start_time`、`end_time`、`order(unique)`、`duration_minutes(自动)`、`is_active`
    - 标准 2 小时时段（建议启用）：
      - 1. 08:00-10:00
      - 2. 10:10-12:10
      - 3. 14:00-16:00
      - 4. 16:10-18:10
      - 5. 19:00-21:00
  - 排课 `Schedule`（`apps/schedules/models.py`）
    - 字段：`course(FK)`、`teacher(FK)`、`classroom(FK)`、`day_of_week∈[1..7]`、`time_slot(FK)`、`week_range(如'1-18')`、`semester`、`academic_year`、`status∈{active,cancelled,...}`
    - 硬约束（数据库唯一）：
      - 同一学期同一时间段：教室唯一（`classroom, day_of_week, time_slot, semester, status=active`）
      - 同一学期同一时间段：教师唯一（`teacher, day_of_week, time_slot, semester, status=active`）

- 业务约束（与算法一致）
  - 仅工作日：只使用 `day_of_week=1..5`（周一到周五），周末无课。
  - 每节课 2 小时：仅选择 `duration_minutes≈120` 的 `TimeSlot`。
  - 每门课每周最多 2 节；每门课单日最多 1 节；避免同日连续。
  - 教室容量需 ≥ 课程最大选课人数。

- 输出要求
  - 以“结构化 JSON”描述待落库的数据集（便于转为管理命令/fixture）：
    - `buildings`: [{ code, name, address? }]
    - `classrooms`: [{ building_code, room_number, capacity, room_type, floor, equipment?, is_active:true }]
    - `users`: {
        teachers: [{ username, full_name?, department, user_type:'teacher' }],
        students: [{ username, full_name?, department, user_type:'student' }]
      }
    - `courses`: [{ code(unique), name, credits, hours, course_type, department, semester:"{{SEMESTER}}", academic_year:"{{ACADEMIC_YEAR}}", max_students, min_students, is_active:true, is_published:true, teachers:[username...], prerequisites:[code...] }]
    - `timeslots`: 若系统已存在 5 个标准 2 小时时段，可仅输出参照清单；如需补齐，请给出 order→(start,end)。
    - `enrollments`: [{ student_username, course_code, status:'enrolled' }]
  - 规模建议：院系 `{{DEPT_COUNT}}`；每院系教师 `{{TEACHERS_PER_DEPT}}`；课程 `{{COURSE_COUNT}}`；教室 `{{CLASSROOM_COUNT}}`；学生 `{{STUDENT_COUNT}}`。

- 质量校验（在 JSON 后附带清单）
  - 课程代码唯一；课程与教师匹配；`max_students >= min_students`；教室容量覆盖课程 `max_students`。
  - `semester/academic_year` 规范化；仅工作日；仅 2 小时时段。
  - 可选：为每门课生成 1-2 条“人工排课示例”，遵守唯一性约束。

- 示例（片段）
```json
{
  "buildings": [{ "code": "A", "name": "一号教学楼" }],
  "classrooms": [{ "building_code": "A", "room_number": "101", "capacity": 80, "room_type": "lecture", "floor": 1, "is_active": true }],
  "users": { "teachers": [{ "username": "t_zhang" }], "students": [{ "username": "s_li" }] },
  "courses": [{ "code": "CS1001", "name": "程序设计", "credits": 3, "hours": 36, "course_type": "required", "department": "计算机学院", "semester": "{{SEMESTER}}", "academic_year": "{{ACADEMIC_YEAR}}", "max_students": 60, "min_students": 10, "is_active": true, "is_published": true, "teachers": ["t_zhang"] }],
  "timeslots": [{ "order": 1, "start": "08:00", "end": "10:00" }],
  "enrollments": [{ "student_username": "s_li", "course_code": "CS1001", "status": "enrolled" }]
}
```
