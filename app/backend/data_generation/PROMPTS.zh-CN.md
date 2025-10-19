# 数据生成提示词模板（排课算法测试专用）

仅用于指导生成“可用于排课算法测试的模拟数据集”的提示词撰写与执行规范。本文件不包含任何代码实现。

---

## 1. 适用范围与输出形式
- **[范围]** 覆盖教学楼/教室、用户（教师/学生）、课程、时间段、课程安排五大类数据。
- **[输出]** 产出单一 JSON 文档，结构与字段严格对齐后端模型；提供统计摘要与自检报告。
- **[一致性]** 所有引用均需可在主表中找到对应实体；遵循唯一性与业务约束（详见第 2 节）。

---

## 2. 模型字段与硬性约束（必须遵守）
- **[User（apps/users/models.py::User）]**
  - `user_type ∈ {admin, academic_admin, teacher, student}`。
  - 教师需具备可辨识字段：`username`、`employee_id`（唯一）、`department`。
- **[Course（apps/courses/models.py::Course）]**
  - 主键字段：`code` 唯一；`name`；`english_name`（可空）。
  - 属性：`credits ∈ [1..10]`，`hours ∈ [1..200]`，`course_type ∈ {required, elective, public, professional}`。
  - 开课信息：`department`、`semester`（例：`2024-2025-1`）、`academic_year`（例：`2024-2025`）。
  - 关系：`teachers` 为教师集合（每个教师必须是 `user_type=teacher`）。
  - 选课限制：`min_students ≤ max_students`。
- **[Building/Classroom（apps/classrooms/models.py）]**
  - `Building`：`code`（唯一）、`name`、`address`（可空）。
  - `Classroom`：`(building, room_number)` 组合唯一；
    - `capacity ≥ 1`；`room_type ∈ {lecture, lab, computer, multimedia, seminar, auditorium, studio, library, gym, other}`；`floor ≥ 1`；
    - `equipment` 为 JSON；`is_available`、`is_active` 为布尔。
- **[TimeSlot（apps/schedules/models.py::TimeSlot）]**
  - `order ∈ [1..20]` 且唯一；`start_time < end_time`；`duration_minutes = end - start`。
- **[Schedule（apps/schedules/models.py::Schedule）]**
  - 关联：`course`、`classroom`、`teacher`（且 `teacher ∈ course.teachers`）、`time_slot`。
  - 时间：`day_of_week ∈ [1..7]`（1=周一，...，7=周日）；`week_range` 例：`1-16周` 或 `1-8,10-16周`；`semester`、`academic_year`。
  - 状态：`status ∈ {active, cancelled, rescheduled, suspended}`，默认 `active`。
  - 关键唯一性（仅对 `status=active` 生效，且在同一 `semester` 内）：
    - 同一 `classroom + day_of_week + time_slot` 唯一。
    - 同一 `teacher + day_of_week + time_slot` 唯一。
  - 容量约束：`classroom.capacity ≥ course.max_students`。

---

## 3. 主提示词（生成完整、无冲突或低冲突数据集）
请严格遵循以下要求，生成面向排课算法测试的 JSON 数据集：
- **[生成目标]** 在给定参数下，生成规模合理、引用一致、满足约束的高质量数据集，用于校验排课算法的可行性与稳定性。
- **[输入参数]**（如未明确则使用默认值）
  - `semester="2024-2025-1"`，`academic_year="2024-2025"`
  - `num_buildings=3`，`num_classrooms=40`（容量分布：小<50、中50-100、大>100）
  - `num_teachers=40`（含多部门）
  - `num_courses=120`（类型配比约：required:elective:public:professional ≈ 3:4:1:2）
  - `days_per_week=5`，`timeslots_per_day=8`，`weeks_total=16`
  - `utilization_level=medium`（课程密度/热门时段占用）
  - `conflict_rate=0%` 或 `1-3%`（低冲突集）
- **[数据一致性规则]**
  - `Course.teachers` 与 `User(user_type=teacher)` 一致；`Schedule.teacher ∈ Course.teachers`。
  - `Classroom.capacity ≥ Course.max_students`；按 `room_type` 与课程性质合理匹配。
  - 任何 `status=active` 的 `Schedule` 均不得违反教师/教室在同一时段的唯一性约束。
  - `TimeSlot.order` 从 1 起连续或近似连续，不得重复；确保 `start_time < end_time`。
- **[周次/时间语法]**
  - `day_of_week ∈ [1..7]`；默认工作日为 1..5，可按参数含周末（6,7）。
  - `week_range` 支持 `"1-16周"`、`"1-8,10-16周"`、`"1,3,5-8周"` 等（允许不带“周”字）。
- **[输出要求]**
  - 产出单一 JSON，字段如下（见第 5 节）并提供 `summary`：
    - 统计条数：楼、教室、教师、课程、时间段、安排；
    - 约束校验统计：教师/教室时段冲突计数、容量违例计数、外键缺失计数；
    - 资源利用率估计（按 timeslot×day 的占用比）。
  - 保留 `seed` 字段以便可重复生成。

---

## 4. 场景子提示词（可选叠加）
- **[S1 无冲突基线]** `conflict_rate=0%`；均衡分配到工作日与各时段，教室容量≥课程上限且预留10%-20%冗余。
- **[S2 低比例冲突]** `conflict_rate=1-5%`；仅在 `status=active` 的层面构造教师或教室的硬冲突（同一 `semester`），并在 `summary` 中显式计数与定位（引用对应 `course_code/teacher_username/building_code/room_number/time_slot_order/day_of_week`）。
- **[S3 资源紧张]** 高利用率（>85%），热门时段（如早 1-2、午 5-6）集中；尽量仍满足容量与唯一性，允许 `min_students` 迫近 `max_students`。
- **[S4 教师负载上限]** 个别教师周课时或日内排布趋于饱和但不越界；避免重复时段冲突。
- **[S5 房间类型匹配]** 实验/机房类课程优先分配 `lab/computer`，大课优先 `auditorium` 或容量更大的 `lecture`。
- **[S6 周末/晚间变体]** 允许 `day_of_week ∈ {6,7}` 与晚间时段；`timeslots_per_day` 可扩至 10-12。
- **[S7 超大规模]** `num_courses ≥ 300`、`num_classrooms ≥ 120`；确保性能压力场景下仍满足约束与一致性。

---

## 5. 输出结构骨架（示例）
```json
{
  "seed": 12345,
  "semester": "2024-2025-1",
  "academic_year": "2024-2025",
  "buildings": [
    {"code": "A", "name": "一号教学楼", "address": "东区"}
  ],
  "classrooms": [
    {"building_code": "A", "room_number": "101", "name": "A101",
     "capacity": 80, "room_type": "lecture", "floor": 1,
     "equipment": {"projector": true, "ac": true},
     "is_available": true, "is_active": true}
  ],
  "users": {
    "teachers": [
      {"username": "t_zhang", "employee_id": "T0001", "department": "计算机学院"}
    ],
    "students": []
  },
  "courses": [
    {"code": "CS101", "name": "程序设计基础", "english_name": "Intro to Programming",
     "credits": 3, "hours": 48, "course_type": "required",
     "department": "计算机学院", "semester": "2024-2025-1", "academic_year": "2024-2025",
     "teacher_usernames": ["t_zhang"], "max_students": 60, "min_students": 20}
  ],
  "time_slots": [
    {"name": "第1节", "start_time": "08:00", "end_time": "08:45", "order": 1, "duration_minutes": 45}
  ],
  "schedules": [
    {"course_code": "CS101", "teacher_username": "t_zhang",
     "building_code": "A", "room_number": "101",
     "time_slot_order": 1, "day_of_week": 1, "week_range": "1-16周",
     "semester": "2024-2025-1", "academic_year": "2024-2025",
     "status": "active", "notes": ""}
  ],
  "summary": {
    "counts": {"buildings": 1, "classrooms": 1, "teachers": 1, "courses": 1, "time_slots": 1, "schedules": 1},
    "violations": {"teacher_timeslot_conflicts": 0, "classroom_timeslot_conflicts": 0, "capacity_violations": 0, "missing_refs": 0},
    "utilization": {"by_day": {"1": 0.5}, "overall": 0.5}
  }
}
```

---

## 6. 命名与分布规范（建议）
- **[课程代码]** 采用院系前缀+编号（如 `CS101`、`MATH201`）。
- **[教学楼与房间]** `Building.code` 简短（A/B/C...），`room_number` 数字或字母数字组合（如 `101`, `B203`）。
- **[时间段]** 早间连续段、午间连续段、晚间连续段；保证 `order` 单调递增且唯一。
- **[分布]**
  - 工作日与时段均衡，或按场景提示产生偏斜（高峰集中）。
  - `week_range` 默认 `1-16周`，亦可产生跳周模式（如 `1-8,10-16周`）。

---

## 7. 自检与验收标准（必须输出并满足）
- **[结构完整]** 包含第 5 节所列所有顶层键，且类型正确。
- **[引用完整]** 所有 `*_code`、`username`、`time_slot_order` 均能在主表找到对应项。
- **[唯一性/容量]** 无 `status=active` 的教师/教室时段重复；无 `capacity < max_students`。
- **[取值范围]**
  - `day_of_week ∈ [1..7]`；`credits ∈ [1..10]`；`hours ∈ [1..200]`；
  - `course_type` 取值合法；`semester/academic_year` 符合格式。
  - `time_slot.order` 唯一；`start_time < end_time`；`duration_minutes = end - start`。
- **[统计报告]** `summary.violations` 中各项均为 0（除非场景刻意注入冲突，则需逐项列出并附最小可复现定位信息）。

---

## 8. 常见错误防范（务必避免）
- **[错配教师]** `Schedule.teacher` 不在 `Course.teachers` 集合内。
- **[错配容量]** 选用容量不足的教室；`capacity < max_students`。
- **[时段重复]** 同一教师/教室在同一 `day_of_week + time_slot` 下多个 `active` 安排。
- **[缺失引用]** `building_code/room_number/course_code/teacher_username/time_slot_order` 无对应主数据。
- **[非法范围]** `day_of_week` 越界、`credits/hours` 越界、时间段不满足先后关系。

---

## 9. 进阶：冲突样本构造（用于算法对抗测试）
当需要生成“低比例冲突集”时：
- 控制 `conflict_rate`（如 1%、3%、5%），随机或定向在热门时段注入冲突；
- 明确冲突类型：
  - `teacher_timeslot_conflict`: 同一教师同一时段重复；
  - `classroom_timeslot_conflict`: 同一教室同一时段重复；
  - `capacity_violation`: 教室容量不足；
- 在 `summary.violations` 计数，并输出 `violations_details` 列表，元素包含：
  `{"type": "teacher_timeslot_conflict", "semester": "2024-2025-1", "day_of_week": 3, "time_slot_order": 2, "teacher_username": "...", "course_codes": ["...","..."]}`。

---

## 10. 可重复性与可追踪性
- 输出 `seed` 与 `parameters`（使用的规模与分布参数），便于复现。
- 输出生成时的时间戳与版本号（可选）。

---

## 11. 执行提示（给数据生成器/LLM 的话术）
- **[严格约束优先]** 如遇冲突，优先满足唯一性与容量等硬性约束；仅在“冲突场景”明确要求时才注入违例样本。
- **[先主表后引用]** 先生成 `buildings/classrooms/users/courses/time_slots`，再生成 `schedules`；引用一律用主表已存在的键。
- **[统计与校验]** 生成完成后，请产出 `summary` 并自检，确保“无冲突集”为 0 违例。
- **[输出唯一文件]** 不要拆分多文件；一次性给出完整 JSON。

---

## 12. 待确认清单（需要产品/业务判定）
- **[每日节次数]** 是否采用 8、10、12 节的标准时段表？是否需要提供学校通用时段模版？
- **[上课日范围]** 是否默认仅周一至周五？周末开课占比约定？
- **[学期周数]** 16 周是否为标准？是否需要 18/20 周变体？
- **[课程类型配比]** 不同院系的课程类型配比是否有既定比例？
- **[容量余量]** 是否要求 `capacity >= max_students + safety_margin`？安全余量比例？
- **[教师负载上限]** 是否存在教师周总学时/日学时软/硬上限，用于生成时做约束？

---
本文件仅为提示词与规范，禁止包含任何实际开发实现或数据导入逻辑。
