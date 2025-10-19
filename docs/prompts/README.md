# 数据模拟与排课算法提示词文档总览

本目录包含用于“大学排课系统”的数据模拟与排课算法开发的中文提示词模板与规范。所有提示词均基于当前代码库模型与约束编写，确保与后端/前端实现一致。

- 参考后端模型与实现
  - 课程模型：`app/backend/apps/courses/models.py` 中 `Course`、`Enrollment` 等
  - 教室模型：`app/backend/apps/classrooms/models.py` 中 `Building`、`Classroom`
  - 排课模型：`app/backend/apps/schedules/models.py` 中 `TimeSlot`、`Schedule`
  - 排课算法：`app/backend/apps/schedules/algorithms.py` 中 `SchedulingAlgorithm`、`create_auto_schedule()`
  - 排课接口：`app/backend/apps/schedules/views.py`（列表、表格、统计、冲突检查、自动排课等）
  - 前端课程表：`app/frontend/src/pages/schedules/ScheduleViewPage.tsx`、`components/education/ScheduleGrid.tsx`

- 目录文件
  - `01_data_simulation_prompt.md`：生成 Buildings/Classrooms/Users/Courses/TimeSlots/Enrollments 的数据模拟提示词
  - `02_scheduling_constraints_prompt.md`：硬/软约束清单与可调权重提示词
  - `03_algorithm_dev_plan_prompt.md`：排课算法开发阶段计划与落地任务提示词
  - `04_evaluation_checklist_prompt.md`：评估指标与验收清单提示词

使用方式：复制各文件提示词为起点，根据场景替换占位符后执行生成/开发/评估流程。
