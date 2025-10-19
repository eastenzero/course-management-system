# 提示词：排课评估与验收清单

- 覆盖率与成功率
  - 课程覆盖率：被排课的课程数 / 待排课课程总数。
  - 成功率：`successful_constraints / total_constraints`（已在 `auto_schedule` 返回）。
  - 失败原因分布：资源不足/容量不足/教师冲突/时间段限制等。

- 分布均衡
  - 按星期分布（应仅周一-周五，周末为 0）。
  - 按时间段分布（避免单一时段过载）。
  - 教师日负载与周负载分布（最高值、均值、中位数）。
  - 教室利用率：`used_classrooms / total_classrooms` 与按容量段的分布。

- 约束一致性
  - 随机抽样 N 条 `Schedule` 检查：教师/教室唯一性、容量校验、教师属于课程、仅 2 小时时段、单日≤1。
  - 校验 `week_range` 合法性（如 `1-18`、`1-8,10-18`）。

- API/前端联调
  - `/schedules/` 支持 `week|weeks` 过滤（列表维度）。
  - `/schedules/table/` 返回 `time_slots + schedule_table`；前端渲染正确。
  - `/schedules/statistics/` 返回统计项完整；参数学期支持规范化。

- 输出要求
  - 给出一组可执行的“评估步骤脚本/伪代码”，涵盖上述四类验证。
  - 产出一份“评估汇总表”（CSV/Markdown），列出核心指标与结论。
