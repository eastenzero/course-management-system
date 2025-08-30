# 智能排课算法系统

## 概述

这是一个完整的智能排课算法系统，采用多种算法策略解决大学课程排课问题。系统集成了遗传算法、贪心算法、局部搜索等多种优化方法，能够处理复杂的约束条件并生成高质量的排课方案。

## 系统架构

```
algorithms/
├── models.py                    # 数据模型定义
├── engine.py                    # 统一排课引擎
├── constraints/                 # 约束条件模块
│   ├── hard_constraints.py     # 硬约束检查
│   ├── soft_constraints.py     # 软约束评分
│   └── manager.py              # 约束管理器
├── genetic/                     # 遗传算法模块
│   ├── individual.py           # 个体表示
│   ├── operators.py            # 遗传操作符
│   └── genetic_algorithm.py    # 遗传算法主类
├── heuristic/                   # 启发式算法模块
│   ├── greedy_scheduler.py     # 贪心排课器
│   ├── priority_rules.py       # 优先级规则
│   └── local_search.py         # 局部搜索
├── conflict/                    # 冲突处理模块
│   ├── detector.py             # 冲突检测器
│   ├── resolver.py             # 冲突解决器
│   └── analyzer.py             # 冲突分析器
├── optimizer/                   # 性能优化模块
│   ├── schedule_optimizer.py   # 排课优化器
│   ├── parallel_ga.py          # 并行遗传算法
│   └── hybrid_optimizer.py     # 混合优化器
├── tests/                       # 测试模块
│   ├── test_models.py          # 模型测试
│   ├── test_constraints.py     # 约束测试
│   └── run_tests.py            # 测试运行器
└── demo.py                     # 演示脚本
```

## 核心功能

### 1. 数据模型
- **Assignment**: 课程分配模型，表示课程、教师、教室、时间的分配关系
- **Conflict**: 冲突模型，表示排课中的各种冲突
- **ScheduleResult**: 排课结果模型，包含完整的排课方案和评估信息
- **TeacherPreference**: 教师偏好模型，表示教师的时间偏好
- **CourseRequirement**: 课程需求模型，表示课程的特殊要求

### 2. 约束条件系统
- **硬约束**: 必须满足的约束条件
  - 教师时间冲突检查
  - 教室时间冲突检查
  - 教室容量检查
  - 教师资格检查
  - 时间段有效性检查
  - 教师工作量限制

- **软约束**: 优化目标，可以违反但会降低方案质量
  - 教师时间偏好评分
  - 工作量平衡评分
  - 时间分布均匀性
  - 教室利用率优化
  - 连续课程惩罚

### 3. 算法模块

#### 遗传算法
- 个体编码：每个个体表示一个完整的排课方案
- 适应度函数：基于硬约束违反和软约束评分
- 选择策略：锦标赛选择、轮盘赌选择、排名选择
- 交叉操作：单点交叉、两点交叉、均匀交叉、基于课程的交叉
- 变异操作：随机变异、交换变异、时间偏移变异、自适应变异

#### 贪心算法
- 基于优先级规则的快速排课
- 支持多种优先级策略：难度优先、约束优先、选课人数优先
- 回溯机制处理失败的分配
- 适合生成初始解

#### 局部搜索
- 邻域操作：时间交换、时间移动、教室更换
- 搜索策略：最佳改进、首次改进、随机搜索
- 用于精细调优排课方案

### 4. 冲突处理
- **冲突检测**: 自动检测各种类型的排课冲突
- **冲突分析**: 分析冲突模式和热点
- **冲突解决**: 多种策略自动解决冲突

### 5. 性能优化
- **并行遗传算法**: 利用多核CPU加速计算
- **混合优化器**: 结合多种算法的优势
- **缓存机制**: 减少重复计算
- **自适应参数**: 根据问题规模调整算法参数

## 使用方法

### 基本使用

```python
from algorithms.engine import SchedulingEngine, AlgorithmType

# 准备数据
courses = [...]  # 课程数据
teachers = [...]  # 教师数据
classrooms = [...]  # 教室数据

# 初始化排课引擎
engine = SchedulingEngine()
engine.initialize(courses, teachers, classrooms)

# 生成排课方案
result = engine.generate_schedule(algorithm=AlgorithmType.HYBRID)

# 查看结果
print(f"适应度评分: {result.fitness_score}")
print(f"冲突数量: {len(result.conflicts)}")
print(f"方案有效性: {result.is_valid}")
```

### 算法选择

```python
# 贪心算法 - 快速生成初始解
result = engine.generate_schedule(algorithm=AlgorithmType.GREEDY)

# 遗传算法 - 高质量优化
result = engine.generate_schedule(algorithm=AlgorithmType.GENETIC)

# 混合算法 - 综合最佳效果
result = engine.generate_schedule(algorithm=AlgorithmType.HYBRID)
```

### 参数配置

```python
# 遗传算法参数
ga_params = {
    'population_size': 100,
    'max_generations': 500,
    'mutation_rate': 0.1,
    'crossover_rate': 0.8,
}

result = engine.generate_schedule(
    algorithm=AlgorithmType.GENETIC,
    algorithm_params=ga_params
)
```

### 结果分析

```python
# 分析排课方案
analysis = engine.analyze_schedule(result)

# 查看资源利用率
resource_analysis = analysis['resource_analysis']
print(f"教师平均负荷: {resource_analysis['teacher_utilization']['average_load']}")
print(f"教室平均使用: {resource_analysis['classroom_utilization']['average_usage']}")
```

## 运行演示

```bash
# 运行演示脚本
cd algorithms
python demo.py
```

演示脚本将展示：
- 不同算法的性能比较
- 排课结果分析
- 冲突检测和解决
- 算法统计信息

## 运行测试

```bash
# 运行所有测试
cd algorithms/tests
python run_tests.py

# 运行特定测试
python run_tests.py test_models
python run_tests.py test_constraints
```

## API接口

系统提供完整的REST API接口：

- `POST /api/algorithms/generate/` - 生成排课方案
- `POST /api/algorithms/analyze/` - 分析排课方案
- `POST /api/algorithms/optimize/` - 优化排课方案
- `GET /api/algorithms/statistics/` - 获取算法统计
- `POST /api/algorithms/export/` - 导出排课结果

## 性能特点

- **高效性**: 遗传算法结合启发式规则，快速收敛到高质量解
- **可扩展性**: 模块化设计，易于添加新的约束条件和算法
- **鲁棒性**: 多层次的错误处理和异常恢复机制
- **灵活性**: 支持多种算法策略和参数配置
- **实用性**: 考虑实际排课需求，处理复杂约束条件

## 技术特色

1. **多算法融合**: 集成遗传算法、贪心算法、局部搜索等多种方法
2. **智能约束处理**: 区分硬约束和软约束，灵活处理各种排课要求
3. **自动冲突解决**: 智能检测和解决排课冲突
4. **性能优化**: 并行计算和缓存机制提升算法效率
5. **可视化分析**: 提供详细的排课分析和统计报告

## 依赖要求

- Python 3.8+
- NumPy
- Django (用于API接口)
- Django REST Framework
- openpyxl (Excel导出)
- reportlab (PDF导出)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进系统功能。

## 联系方式

如有问题或建议，请联系开发团队。
