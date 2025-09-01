# 大规模数据生成与导入设计方案

## 概述

针对系统当前的几十万学生数据，设计一套完整的课程、教室、排课数据生成与导入方案，确保生成的数据规模合理、约束关系正确，并能够支持智能排课算法的有效运行。

## 技术架构

### 数据生成架构

```mermaid
graph TD
    subgraph "数据分析层"
        A[现有数据分析] --> B[规模测算]
        B --> C[约束关系建模]
    end
    
    subgraph "生成引擎层"
        D[教师数据生成器] --> E[课程数据生成器]
        E --> F[教室数据生成器]
        F --> G[排课数据生成器]
        G --> H[选课数据生成器]
    end
    
    subgraph "约束验证层"
        I[硬约束验证器]
        J[软约束评估器]
        K[冲突检测器]
    end
    
    subgraph "导入执行层"
        L[批量导入器]
        M[进度监控器]
        N[数据校验器]
    end
    
    C --> D
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
```

### 核心约束关系模型

```mermaid
erDiagram
    STUDENT ||--o{ ENROLLMENT : enrolls
    COURSE ||--o{ ENROLLMENT : has
    COURSE ||--o{ SCHEDULE : scheduled
    TEACHER ||--o{ COURSE : teaches
    CLASSROOM ||--o{ SCHEDULE : hosts
    TIMESLOT ||--o{ SCHEDULE : uses
    DEPARTMENT ||--o{ COURSE : offers
    DEPARTMENT ||--o{ TEACHER : employs
    BUILDING ||--o{ CLASSROOM : contains
    
    STUDENT {
        int id PK
        string student_id UK
        string department
        string major
        int enrollment_year
    }
    
    TEACHER {
        int id PK
        string teacher_id UK
        string department
        string title
        int max_weekly_hours
    }
    
    COURSE {
        int id PK
        string code UK
        string name
        int credits
        int hours
        string course_type
        int max_students
        int min_students
    }
    
    CLASSROOM {
        int id PK
        string room_number
        int capacity
        string room_type
        string building
    }
    
    SCHEDULE {
        int id PK
        int course_id FK
        int teacher_id FK
        int classroom_id FK
        int timeslot_id FK
        string semester
    }
```

## 数据规模规划

### 基础数据规模计算

基于现有数据规模（851,064个学生），按照高校标准比例计算：

| 数据类型 | 计算依据 | 目标数量 | 说明 |
|---------|----------|----------|------|
| 学生 | 现有数据 | 851,064 | 保持现有规模 |
| 教师 | 师生比 1:15 | 56,738 | 标准师生比例 |
| 课程 | 专业课程配置 | 15,000 | 覆盖所有专业需求 |
| 教室 | 容量利用率 80% | 3,500 | 满足排课需求 |
| 排课记录 | 课程×时间段 | 180,000 | 学期课程安排 |
| 选课记录 | 学生×平均选课 | 5,950,448 | 每生平均7门课 |

### 分层数据生成策略

```mermaid
flowchart TD
    A[阶段1: 基础设施数据] --> B[阶段2: 用户数据]
    B --> C[阶段3: 课程数据]
    C --> D[阶段4: 排课数据]
    D --> E[阶段5: 选课数据]
    
    A1[教学楼: 50栋] --> A2[教室: 3,500间]
    A2 --> A3[时间段: 70个]
    
    B1[院系: 25个] --> B2[专业: 120个]
    B2 --> B3[教师: 56,738名]
    
    C1[课程分类生成] --> C2[先修关系建立]
    C2 --> C3[教师分配]
    
    D1[约束检查] --> D2[冲突避免]
    D2 --> D3[优化分配]
    
    E1[容量控制] --> E2[先修检查]
    E2 --> E3[时间冲突避免]
```

## 数据生成模型

### 教师数据生成器

```mermaid
classDiagram
    class TeacherGenerator {
        +int target_count
        +List~Department~ departments
        +Dict distribution_config
        +generate_teachers() List~Teacher~
        +calculate_department_distribution()
        +generate_teacher_profile()
        +assign_teaching_capacity()
        +validate_workload_constraints()
    }
    
    class TeacherProfile {
        +string teacher_id
        +string name
        +string department
        +string title
        +int max_weekly_hours
        +List~string~ specialties
        +Dict time_preferences
    }
    
    TeacherGenerator --> TeacherProfile : creates
```

### 课程数据生成器

```mermaid
classDiagram
    class CourseGenerator {
        +int target_count
        +List~Teacher~ teachers
        +List~Department~ departments
        +generate_courses() List~Course~
        +create_course_hierarchy()
        +assign_prerequisites()
        +allocate_teachers()
        +validate_course_constraints()
    }
    
    class CourseProfile {
        +string code
        +string name
        +int credits
        +string course_type
        +string department
        +int max_students
        +List~string~ prerequisites
        +List~Teacher~ assigned_teachers
    }
    
    CourseGenerator --> CourseProfile : creates
```

### 教室数据生成器

```mermaid
classDiagram
    class ClassroomGenerator {
        +int target_count
        +List~Building~ buildings
        +generate_classrooms() List~Classroom~
        +create_building_layout()
        +assign_room_types()
        +calculate_capacity_distribution()
        +validate_space_requirements()
    }
    
    class ClassroomProfile {
        +string room_number
        +string building
        +int capacity
        +string room_type
        +Dict equipment
        +boolean is_available
    }
    
    ClassroomGenerator --> ClassroomProfile : creates
```

## 约束管理系统

### 硬约束验证

```mermaid
flowchart TD
    A[硬约束验证器] --> B[教师时间冲突检查]
    A --> C[教室时间冲突检查]
    A --> D[容量约束检查]
    A --> E[资质要求检查]
    
    B --> B1[同一教师同一时间只能在一个地点]
    C --> C1[同一教室同一时间只能有一门课]
    D --> D1[教室容量 >= 选课人数]
    E --> E1[教师专业匹配课程要求]
    
    B1 --> F[约束违反报告]
    C1 --> F
    D1 --> F
    E1 --> F
```

### 软约束优化

| 约束类型 | 权重 | 评分标准 | 优化目标 |
|---------|------|----------|----------|
| 教师时间偏好 | 0.3 | 偏好时间段分配率 | 最大化教师满意度 |
| 教室利用率 | 0.25 | 空间利用效率 | 均衡教室使用 |
| 学生课程分布 | 0.2 | 时间分散程度 | 避免课程集中 |
| 连续课程安排 | 0.15 | 相关课程邻近性 | 教学连贯性 |
| 跨校区移动 | 0.1 | 位置转换时间 | 减少移动成本 |

## 数据导入流程

### 批量导入策略

```mermaid
sequenceDiagram
    participant Client as 导入客户端
    participant Validator as 数据验证器
    participant Processor as 批处理器
    participant DB as 数据库
    participant Monitor as 监控系统
    
    Client->>Validator: 提交生成数据
    Validator->>Validator: 执行约束验证
    Validator->>Processor: 验证通过的数据
    
    loop 批量处理
        Processor->>DB: 插入数据批次
        DB->>Monitor: 返回执行状态
        Monitor->>Client: 更新进度信息
    end
    
    Processor->>Validator: 最终一致性检查
    Validator->>Client: 导入完成报告
```

### 性能优化方案

| 优化策略 | 实施方法 | 预期效果 |
|---------|----------|----------|
| 批量插入 | 每批5000条记录 | 提升插入速度10倍 |
| 索引优化 | 导入前禁用，导入后重建 | 减少写入时间50% |
| 事务管理 | 分段提交，避免长事务 | 降低锁定时间 |
| 并行处理 | 多线程处理不同表 | 提升整体效率30% |
| 内存管理 | 数据流式处理 | 控制内存使用 |

## 数据质量保障

### 数据完整性验证

```mermaid
flowchart TD
    A[数据完整性检查] --> B[外键关系验证]
    A --> C[唯一约束检查]
    A --> D[必填字段验证]
    A --> E[数据范围验证]
    
    B --> B1[课程-教师关联]
    B --> B2[排课-教室关联]
    B --> B3[选课-学生关联]
    
    C --> C1[学号唯一性]
    C --> C2[教师编号唯一性]
    C --> C3[课程代码唯一性]
    
    D --> D1[基础信息完整]
    D --> D2[关键字段非空]
    
    E --> E1[数值范围合理]
    E --> E2[时间数据有效]
```

### 业务逻辑验证

| 验证项目 | 验证规则 | 错误处理 |
|---------|----------|----------|
| 师生比例 | 1:10 - 1:20 | 警告并调整 |
| 课程容量 | 20-200人 | 自动修正 |
| 教师工作量 | 每周8-20学时 | 重新分配 |
| 教室利用率 | 60%-85% | 优化调整 |
| 时间冲突 | 零冲突原则 | 强制解决 |

## 监控与报告

### 实时监控指标

```mermaid
dashboard
    title 数据生成导入监控面板
    
    section 进度监控
        生成进度: 75: [0, 100]
        导入进度: 45: [0, 100]
        验证进度: 60: [0, 100]
    
    section 性能指标
        生成速度: 15000: [0, 50000]
        导入速度: 8500: [0, 20000]
        错误率: 0.02: [0, 0.1]
    
    section 资源使用
        内存使用: 68: [0, 100]
        CPU使用: 45: [0, 100]
        磁盘IO: 75: [0, 100]
```

### 质量报告模板

| 指标类别 | 具体指标 | 目标值 | 实际值 | 状态 |
|---------|----------|-------|-------|------|
| 数据规模 | 教师总数 | 56,738 | - | 待生成 |
| 数据规模 | 课程总数 | 15,000 | - | 待生成 |
| 数据规模 | 教室总数 | 3,500 | - | 待生成 |
| 约束合规 | 硬约束违反率 | 0% | - | 待验证 |
| 约束合规 | 软约束满足率 | >80% | - | 待评估 |
| 性能指标 | 生成用时 | <2小时 | - | 待执行 |
| 性能指标 | 导入用时 | <1小时 | - | 待执行 |

## 实施计划

### 开发阶段

```mermaid
gantt
    title 数据生成导入系统实施计划
    dateFormat  YYYY-MM-DD
    section 分析设计
    需求分析           :done, analysis, 2024-01-01, 2024-01-03
    架构设计           :done, design, 2024-01-04, 2024-01-06
    
    section 开发实现
    生成器开发         :active, dev1, 2024-01-07, 2024-01-14
    约束系统开发       :dev2, 2024-01-10, 2024-01-17
    导入器开发         :dev3, 2024-01-15, 2024-01-20
    
    section 测试验证
    单元测试           :test1, 2024-01-18, 2024-01-22
    集成测试           :test2, 2024-01-21, 2024-01-25
    性能测试           :test3, 2024-01-24, 2024-01-28
    
    section 部署运行
    生产环境部署       :deploy, 2024-01-29, 2024-01-30
    数据生成执行       :exec, 2024-01-31, 2024-02-01
```

### 风险控制

| 风险类型 | 风险描述 | 影响程度 | 应对策略 |
|---------|----------|----------|----------|
| 性能风险 | 大数据量导致内存溢出 | 高 | 分批处理+内存监控 |
| 数据风险 | 约束冲突导致生成失败 | 中 | 智能约束解决器 |
| 时间风险 | 生成时间超出预期 | 中 | 并行化+性能优化 |
| 质量风险 | 生成数据不符合业务需求 | 高 | 多层验证+回滚机制 |

## 技术实现

### 核心算法

#### 智能排课算法集成

```mermaid
flowchart TD
    A[排课请求] --> B{算法选择}
    B -->|小规模| C[贪心算法]
    B -->|中等规模| D[遗传算法]
    B -->|大规模| E[并行遗传算法]
    B -->|复杂约束| F[混合算法]
    
    C --> G[约束验证]
    D --> G
    E --> G
    F --> G
    
    G --> H{验证通过?}
    H -->|是| I[输出排课方案]
    H -->|否| J[冲突解决]
    J --> G
```

#### 数据一致性保证

```mermaid
stateDiagram-v2
    [*] --> 准备阶段
    准备阶段 --> 数据验证 : 开始生成
    数据验证 --> 约束检查 : 验证通过
    数据验证 --> 错误处理 : 验证失败
    约束检查 --> 批量导入 : 约束满足
    约束检查 --> 约束解决 : 约束冲突
    约束解决 --> 约束检查 : 冲突解决
    批量导入 --> 最终验证 : 导入完成
    最终验证 --> 完成 : 验证通过
    最终验证 --> 回滚 : 验证失败
    错误处理 --> 数据验证 : 修复后重试
    回滚 --> 准备阶段 : 回滚完成
    完成 --> [*]
```

### 关键代码结构

#### 主生成器接口

```python
class MassDataGenerator:
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.constraint_manager = ConstraintManager()
        self.progress_monitor = ProgressMonitor()
    
    def generate_complete_dataset(self) -> DatasetResult:
        """生成完整数据集"""
        pass
    
    def validate_constraints(self, dataset: Dataset) -> ValidationResult:
        """验证约束条件"""
        pass
    
    def import_to_database(self, dataset: Dataset) -> ImportResult:
        """导入到数据库"""
        pass
```

#### 约束管理器

```python
class ConstraintManager:
    def __init__(self):
        self.hard_constraints = HardConstraints()
        self.soft_constraints = SoftConstraints()
    
    def validate_schedule(self, schedule: Schedule) -> ConstraintResult:
        """验证排课方案"""
        pass
    
    def resolve_conflicts(self, conflicts: List[Conflict]) -> Resolution:
        """解决约束冲突"""
        pass
```

### 配置管理

#### 生成配置

```yaml
generation_config:
  scale:
    students: 851064
    teachers: 56738
    courses: 15000
    classrooms: 3500
    
  constraints:
    teacher_student_ratio: [10, 20]
    class_capacity: [20, 200]
    teacher_weekly_hours: [8, 20]
    
  optimization:
    algorithm: "genetic"
    population_size: 100
    max_generations: 500
    mutation_rate: 0.1
    
  import:
    batch_size: 5000
    max_retries: 3
    transaction_timeout: 300
```

## 验收标准

### 功能验收

| 功能项 | 验收标准 | 测试方法 |
|-------|----------|----------|
| 数据生成 | 按规模要求生成完整数据 | 自动化测试 |
| 约束验证 | 硬约束100%满足 | 约束检查器 |
| 性能要求 | 生成+导入<3小时 | 性能测试 |
| 数据质量 | 业务逻辑正确性>95% | 抽样验证 |
| 系统稳定 | 连续运行不出错 | 压力测试 |

### 质量验收

| 质量指标 | 目标值 | 验收方法 |
|---------|-------|----------|
| 代码覆盖率 | >85% | 单元测试 |
| 文档完整性 | 100% | 文档审查 |
| 错误处理 | 完整覆盖 | 异常测试 |
| 用户体验 | 操作简便 | 用户测试 |
| 可维护性 | 易于扩展 | 代码审查 |