# 真实课程数据生成器使用指南

## 概述

本系统基于课程安排合理性标准，实现了约束感知的百万级课程数据生成，确保生成的数据符合真实教学场景的业务逻辑和时间安排规律。

## 核心特性

### 1. 课程安排合理性标准
- **时间段分布合理性**: 黄金时段(8:00-11:40)优先安排核心课程
- **先修课程逻辑**: 严格的课程依赖关系和学期间隔要求
- **教师-课程匹配**: 基于专业领域、职称、经验的智能匹配
- **资源容量约束**: 教室容量与选课人数的合理匹配

### 2. 数据生成约束
- **硬约束**: 时间冲突、容量限制、先修关系
- **软约束**: 教师偏好、课程分布均衡性
- **真实性约束**: 课程命名、学分学时、专业匹配

### 3. 百万级处理能力
- **分批处理**: 2000条/批的智能分批机制
- **内存优化**: 对象池、垃圾回收、流式处理
- **并行处理**: 支持线程/进程并行和混合模式
- **检查点**: 自动保存和恢复机制

## 快速开始

### 安装依赖
```bash
pip install networkx pandas numpy psutil rich
```

### 基本使用

1. **小规模测试数据（推荐新手）**
```bash
python realistic_course_generator.py --students 1000 --teachers 50 --courses 200
```

2. **中等规模数据**
```bash
python realistic_course_generator.py --students 50000 --teachers 2500 --courses 5000
```

3. **百万级数据生成**
```bash
python realistic_course_generator.py --students 1000000 --teachers 50000 --courses 100000 --batch-size 5000 --workers 8
```

### 高级配置

4. **高真实性模式**
```bash
python realistic_course_generator.py --students 10000 --realism-level 0.95 --constraint-strictness 0.9
```

5. **性能优化模式**
```bash
python realistic_course_generator.py --students 100000 --batch-size 10000 --max-memory 8192 --workers 12
```

6. **灵活约束模式**
```bash
python realistic_course_generator.py --students 50000 --disable-time-conflicts --disable-workload
```

## 参数说明

### 数据规模参数
- `--students`: 目标学生数量
- `--teachers`: 目标教师数量  
- `--courses`: 目标课程数量
- `--schedules`: 目标排课记录数量
- `--semesters`: 学期数量(默认8)

### 质量控制参数
- `--realism-level`: 真实性要求等级(0-1,默认0.8)
- `--constraint-strictness`: 约束严格程度(0-1,默认0.9)

### 约束开关
- `--disable-prerequisites`: 禁用先修课程约束
- `--disable-time-conflicts`: 禁用时间冲突检测
- `--disable-capacity`: 禁用容量约束
- `--disable-workload`: 禁用教师工作负荷限制

### 性能优化参数
- `--batch-size`: 批处理大小(默认2000)
- `--max-memory`: 最大内存限制MB(默认4096)
- `--workers`: 并行工作进程数(默认4)
- `--checkpoint-interval`: 检查点保存间隔(默认10000)

## 输出说明

### 数据文件
- `course_dataset.json`: 主数据文件(小规模)
- `final_dataset.json`: 最终数据集(大规模)
- `generation_report.json`: 生成报告

### 报告内容
```json
{
  "generation_summary": {
    "total_time_seconds": 120.5,
    "generation_mode": "平衡模式",
    "constraint_compliance": {...}
  },
  "data_statistics": {
    "total_teachers": 5000,
    "total_courses": 10000,
    "total_schedules": 500000
  },
  "quality_assessment": {
    "overall_score": 0.891,
    "critical_issues": 5,
    "recommendations": [...]
  }
}
```

## 数据质量指标

### 质量维度
1. **完整性**(Completeness): 必要字段完整度
2. **一致性**(Consistency): 外键关系和业务逻辑一致性
3. **准确性**(Accuracy): 数值范围和格式准确性
4. **唯一性**(Uniqueness): 主键唯一性验证

### 质量等级
- **优秀**: 总分≥0.9，严重问题=0
- **良好**: 总分≥0.8，严重问题≤5
- **可接受**: 总分≥0.7，严重问题≤20
- **需改进**: 总分<0.7或严重问题>20

## 课程安排合理性验证

### 时间约束验证
- 黄金时段(上午)优先安排必修课和核心课程
- 下午时段安排实验课和实践类课程
- 晚间时段安排选修课和补充课程
- 避免连续超过4节课的安排

### 先修关系验证
- 数学基础课程递进：高等数学→线性代数→概率统计
- 计算机课程链：程序设计→数据结构→算法设计
- 学期间隔：先修课程至少提前1学期

### 教师匹配验证
- 教授：研究生课程和核心专业课
- 副教授：专业必修课和部分选修课
- 讲师：基础课程和通识教育课程
- 专业匹配度≥70%为合理匹配

## 故障排除

### 常见问题

1. **内存不足**
```bash
# 减少批次大小和内存限制
python realistic_course_generator.py --batch-size 1000 --max-memory 2048
```

2. **生成速度慢**
```bash
# 增加并行度，禁用部分约束
python realistic_course_generator.py --workers 8 --disable-time-conflicts
```

3. **约束冲突过多**
```bash
# 降低约束严格程度
python realistic_course_generator.py --constraint-strictness 0.7
```

4. **质量分数偏低**
```bash
# 提高真实性要求，启用所有约束
python realistic_course_generator.py --realism-level 0.9 --constraint-strictness 0.95
```

### 性能调优建议

**系统配置推荐**:
- 小规模(<1万学生): 4GB内存，2核CPU
- 中等规模(1-10万学生): 8GB内存，4核CPU
- 大规模(10万+学生): 16GB内存，8核以上CPU

**参数优化**:
```bash
# 高性能配置
--batch-size 5000 --max-memory 8192 --workers 8 --gc-frequency 10

# 保守配置  
--batch-size 1000 --max-memory 2048 --workers 2 --gc-frequency 3
```

## 扩展开发

### 自定义约束
可以在 `course_scheduling_constraints.py` 中添加新的约束规则：

```python
def custom_constraint_check(self, course, teacher, schedule):
    # 自定义约束逻辑
    return validation_result
```

### 自定义数据生成
可以在 `constraint_aware_generator.py` 中扩展生成逻辑：

```python
def generate_custom_data(self):
    # 自定义数据生成逻辑
    return custom_data
```

## 技术支持

如遇问题，请检查：
1. 日志文件 `course_generation.log`
2. 生成报告中的错误信息和建议
3. 系统资源使用情况

建议在正式使用前先进行小规模测试，验证配置参数的合理性。