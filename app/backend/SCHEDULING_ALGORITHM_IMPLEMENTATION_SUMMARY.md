# 智能排课算法系统实现总结

## 项目概述

本项目实现了一个完整的智能排课算法系统，支持处理数千门课程的大规模排课需求。系统提供了三种不同的算法实现：

1. **贪心算法** - 基础算法，快速但可能不是最优解
2. **遗传算法** - 全局优化算法，寻找近似最优解
3. **混合算法** - 结合贪心算法和遗传算法的优势

## 功能特性

### 1. 算法实现

#### 贪心算法 (Greedy Algorithm)
- 基于约束满足问题(CSP)的实现
- 支持超时控制
- 增强的约束处理能力
- 支持多种约束类型：
  - 时间偏好约束
  - 教室偏好约束
  - 教师偏好约束
  - 避免连续排课
  - 避免中午时间
  - 每日最大课时限制
  - 固定时间槽约束

#### 遗传算法 (Genetic Algorithm)
- 基于种群的进化算法
- 支持自定义种群大小、进化代数等参数
- 完整的遗传操作：
  - 选择（锦标赛选择）
  - 交叉（均匀交叉）
  - 变异（随机变异）
- 适应度函数设计，综合考虑：
  - 硬约束满足度
  - 软约束满足度
  - 优化目标（资源平衡等）

#### 混合算法 (Hybrid Algorithm)
- 结合贪心算法和遗传算法的优势
- 三阶段优化过程：
  1. 贪心算法生成初始解
  2. 遗传算法全局优化
  3. 局部优化改进
- 支持超时控制和参数调优

### 2. 性能优化

- 大规模数据处理优化
- 冲突检测性能优化（O(1)时间复杂度）
- 超时控制机制
- 资源利用率统计和分析

### 3. API接口

#### 排课算法API
- `/api/scheduling/run-algorithm/` - 运行指定算法
- `/api/scheduling/apply-results/` - 应用排课结果
- `/api/scheduling/status/` - 获取排课状态
- `/api/scheduling/validate-constraints/` - 验证约束条件

#### 性能对比API
- `/api/scheduling/compare-algorithms/` - 比较不同算法性能

#### 可视化API
- `/api/scheduling/visualization/schedule-table/` - 获取课程表
- `/api/scheduling/visualization/statistics/` - 获取统计图表
- `/api/scheduling/visualization/conflicts/` - 获取冲突报告

### 4. 可视化功能

- 课程表展示
- 统计图表（星期分布、时间段分布、课程类型分布等）
- 冲突报告
- 资源利用率分析

### 5. 测试和优化工具

- 算法性能对比工具
- 大规模数据测试脚本
- 参数优化工具

## 技术实现

### 核心类结构

```
SchedulingAlgorithm (基础类)
├── GeneticSchedulingAlgorithm (遗传算法)
└── HybridSchedulingAlgorithm (混合算法)
```

### 主要数据结构

- `ScheduleConstraint` - 排课约束
- `ScheduleSlot` - 排课时间槽
- `Individual` - 遗传算法个体

### 约束处理

系统支持多种约束类型，包括硬约束和软约束：

1. **硬约束**（必须满足）
   - 教师时间冲突
   - 教室时间冲突
   - 课程容量约束

2. **软约束**（尽量满足）
   - 时间偏好
   - 教室偏好
   - 教师偏好
   - 连续排课避免

## 使用方法

### 1. 通过API调用

```bash
# 运行贪心算法
curl -X POST /api/scheduling/run-algorithm/ \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm_type": "greedy",
    "semester": "2024春",
    "academic_year": "2023-2024"
  }'

# 运行遗传算法
curl -X POST /api/scheduling/run-algorithm/ \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm_type": "genetic",
    "semester": "2024春",
    "academic_year": "2023-2024"
  }'

# 运行混合算法
curl -X POST /api/scheduling/run-algorithm/ \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm_type": "hybrid",
    "semester": "2024春",
    "academic_year": "2023-2024"
  }'
```

### 2. 通过Python代码调用

```python
from apps.schedules.algorithms import create_auto_schedule
from apps.schedules.genetic_algorithm import create_genetic_schedule
from apps.schedules.hybrid_algorithm import create_hybrid_schedule

# 贪心算法
result = create_auto_schedule("2024春", "2023-2024", algorithm_type="greedy")

# 遗传算法
result = create_genetic_schedule("2024春", "2023-2024")

# 混合算法
result = create_hybrid_schedule("2024春", "2023-2024")
```

## 性能特点

### 大规模数据处理能力
- 支持数千门课程的排课需求
- 优化的数据结构和算法设计
- 超时控制机制防止长时间阻塞

### 算法性能对比
根据测试结果，三种算法在不同场景下各有优势：

1. **贪心算法**：速度最快，适合快速生成初步排课方案
2. **遗传算法**：解质量最高，适合对排课质量要求较高的场景
3. **混合算法**：平衡了速度和质量，是大多数场景下的推荐选择

## 部署和维护

### 测试脚本
项目包含多个测试脚本：
- `test_scheduling_algorithms.py` - 基本算法测试
- `test_large_scale_scheduling.py` - 大规模数据测试
- `optimize_algorithm_parameters.py` - 参数优化

### 参数调优
使用`optimize_algorithm_parameters.py`脚本可以找到最适合特定数据集的算法参数。

## 总结

本项目成功实现了完整的智能排课算法系统，具备以下特点：

1. **多种算法选择**：提供贪心、遗传、混合三种算法
2. **大规模数据支持**：能够处理数千门课程的排课需求
3. **丰富的约束处理**：支持多种硬约束和软约束
4. **完善的API接口**：提供RESTful API供前端调用
5. **可视化功能**：支持排课结果的可视化展示
6. **性能优化**：针对大规模数据进行了多项优化
7. **测试和调优工具**：提供完整的测试和参数优化工具

系统已经准备好投入实际使用，能够满足教育机构的复杂排课需求。