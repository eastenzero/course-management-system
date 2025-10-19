# 数据生成模块（文档与提示词，仅供规划）

本目录提供用于“排课算法”测试所需的模拟数据生成之规划与提示词模板，严格对齐现有后端数据模型字段与约束，避免因模拟数据失真导致算法评测失效。当前交付仅包含文档与提示词，不含任何实际代码与实现。

## 目标
- **[一致性]** 生成数据需与现有模型字段、取值范围、唯一性与业务约束完全一致。
- **[可控性]** 支持通过参数控制规模、冲突比例、资源紧张度等，以便覆盖不同测试场景。
- **[可验证性]** 输出应满足可校验的结构化格式（建议 JSON），并附带校验清单。

## 适配的核心模型与关键字段
以下内容摘自后端模型文件，务必保持一致：
- **[用户 `apps/users/models.py::User`]**
  - `user_type`: `admin|academic_admin|teacher|student`
  - `employee_id`(教师/管理员)、`student_id`(学生)
  - `department`
- **[课程 `apps/courses/models.py::Course`]**
  - 基本: `code`(唯一)、`name`、`english_name`
  - 属性: `credits`(1-10)、`hours`(1-200)、`course_type`(`required|elective|public|professional`)
  - 开课: `department`、`semester`(如 `2024-2025-1`)、`academic_year`(`2024-2025`)
  - 关系: `teachers`(ManyToMany，限定 `user_type=teacher`)
  - 限制: `max_students`、`min_students`，`min_students <= max_students`
- **[教学楼与教室 `apps/classrooms/models.py::Building`, `Classroom`]**
  - `Building`: `code`(唯一)、`name`、`address`
  - `Classroom` 基本: `building`、`room_number`(与 `building` 组合唯一)、`name`
  - 属性: `capacity`(>=1)、`room_type`(`lecture|lab|computer|multimedia|seminar|auditorium|studio|library|gym|other`)、`floor`
  - 其他: `equipment`(JSON)、`is_available`、`is_active`
- **[时间段 `apps/schedules/models.py::TimeSlot`]**
  - `name`(如“第1节课”)、`start_time`、`end_time`、`order`(唯一, 1-20)
  - `duration_minutes` 可由 `start_time/end_time`推导
- **[课程安排 `apps/schedules/models.py::Schedule`]**
  - 关联: `course`、`classroom`、`teacher`(必须属于 `course.teachers`)、`time_slot`
  - 时间: `day_of_week`(1-7)、`week_range`(如 `1-16周`、`1-8,10-16周`)、`semester`、`academic_year`
  - 状态: `status`(`active|cancelled|rescheduled|suspended`，默认 `active`)
  - 关键约束：
    - 同一`semester`里，同一`classroom + day_of_week + time_slot`在`status=active`下唯一
    - 同一`semester`里，同一`teacher + day_of_week + time_slot`在`status=active`下唯一
    - `classroom.capacity >= course.max_students`

## 数据集组成建议
- **[规模参数]**
  - `num_buildings`: 2-6
  - `num_classrooms`: 20-80（容量分布：小 <50、中 50-100、大 >100）
  - `num_teachers`: 20-60（含部门分布）
  - `num_courses`: 40-200（类型分布：必修/选修/公共/专业 ≈ 3:4:1:2，可按需调整）
  - `days_per_week`: 5 或 6（是否含周末需确认）
  - `timeslots_per_day`: 6-12（如早 1-4、午 5-8、晚 9-12）
  - `weeks_total`: 16 或 18（`week_range` 默认如 `1-16周`）
- **[负载与冲突]**
  - `utilization_level`: 低/中/高（影响班级密度与排满程度）
  - `conflict_rate`: 0、1%、5%、10%...（用于构造冲突样本，校验冲突检测能力）
- **[关联策略]**
  - 课程与教师：1:1 或 1:n，且 `Schedule.teacher ∈ Course.teachers`
  - 课程与教室：按 `capacity` 与 `room_type` 匹配
  - `Schedule` 生成需满足教师/教室时段唯一性

## 输出格式与文件约定（建议）
- **[单一 JSON 文件]** 便于一次性导入与校验：
```json
{
  "semester": "2024-2025-1",
  "academic_year": "2024-2025",
  "buildings": [
    {"code": "A", "name": "一号教学楼", "address": "校区东区"}
  ],
  "classrooms": [
    {"building_code": "A", "room_number": "101", "capacity": 80, "room_type": "lecture", "floor": 1,
     "name": "A101", "equipment": {"projector": true, "ac": true}, "is_available": true, "is_active": true}
  ],
  "users": {
    "teachers": [
      {"username": "t_zhang", "employee_id": "T0001", "department": "计算机学院"}
    ],
    "students": []
  },
  "courses": [
    {"code": "CS101", "name": "程序设计基础", "credits": 3, "hours": 48, "course_type": "required",
     "department": "计算机学院", "semester": "2024-2025-1", "academic_year": "2024-2025",
     "teacher_usernames": ["t_zhang"], "max_students": 60, "min_students": 20}
  ],
  "time_slots": [
    {"name": "第1节", "start_time": "08:00", "end_time": "08:45", "order": 1, "duration_minutes": 45}
  ],
  "schedules": [
    {"course_code": "CS101", "teacher_username": "t_zhang", "building_code": "A", "room_number": "101",
     "time_slot_order": 1, "day_of_week": 1, "week_range": "1-16周",
     "semester": "2024-2025-1", "academic_year": "2024-2025", "status": "active"}
  ]
}
```
- **[引用约定]**
  - `Classroom` 通过 `building_code + room_number` 唯一标识
  - `Teacher` 通过 `username` 或 `employee_id` 标识（与 `users.User` 一致）
  - `Course` 通过 `code` 唯一标识
  - `TimeSlot` 通过 `order` 唯一标识

## 校验清单（生成后必须满足）
- **[结构校验]** JSON 必须包含 `buildings/classrooms/users/courses/time_slots/schedules` 关键数组或对象段。
- **[字段校验]** 取值范围、格式严格遵循模型：
  - `day_of_week ∈ [1..7]`
  - `semester` 形如 `YYYY-YYYY-N`
  - `academic_year` 形如 `YYYY-YYYY`
  - `week_range` 形如 `1-16周` 或 `1-8,10-16周`（允许逗号分段、连字符范围、可无“周”字）
  - `time_slot.order` 唯一，`start_time < end_time`
- **[业务校验]**
  - `Schedule.teacher ∈ Course.teachers`
  - `Classroom.capacity >= Course.max_students`
  - 同一 `semester` 内：
    - 同一 `classroom + day_of_week + time_slot` 下 `status=active` 唯一
    - 同一 `teacher + day_of_week + time_slot` 下 `status=active` 唯一
- **[一致性校验]** 所有外键或引用字段均可在对应主表中找到。

## 典型测试场景预设
- **[无冲突基础集]** 验证算法在无冲突条件下的输出稳定性与性能基线。
- **[低比例冲突集]** 注入 1%-5% 硬冲突，验证冲突检测与解冲能力。
- **[资源紧张集]** 教室容量与数量紧张、热门时段拥挤，检验资源分配策略。
- **[教师负载上限集]** 控制教师周负载/日负载接近上限，测试可行性与权衡。

## 与现有脚本/文档的关系（只读参考）
- 相关参考文件（不修改不运行）：
  - `backend/create_large_scale_data.py`
  - `backend/generate_mock_data.py`
  - `backend/import_*` 与 `backend/run_scheduling_algorithm.py`
  - `backend/SCHEDULING_ALGORITHM_USAGE_GUIDE.md`

## 使用方式（建议流程，非实现）
- 使用 `PROMPTS.zh-CN.md` 中的提示词，在您偏好的数据生成工具中产出 JSON。
- 依据“校验清单”进行自检，必要时微调参数（规模、冲突率等）再生成。
- 后续如需导入或联调，可在单独任务中进行，当前不包含任何实现动作。

## 待确认事项
- **[时段设置]** 每日节次数量与时间表是否有校规标准？是否需要统一 8、10 或 12 节？
- **[上课日]** 是否仅周一至周五？周末是否可能安排课程？
- **[学期长度]** 默认 16 周是否合适？是否需要 18 或 20 周？
- **[部门/学院]** 是否有标准院系列表与课程类型配比？
- **[冲突策略]** 是否需要单独输出“冲突样本集”与“无冲突样本集”？默认冲突率建议是多少？
- **[容量策略]** 是否允许课程的 `max_students` 接近或等于教室容量，或需保留安全余量？

---
本目录仅用于文档与提示词沉淀，不包含任何代码实现或数据写入逻辑。
