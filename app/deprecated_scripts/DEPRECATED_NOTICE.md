# 弃用脚本说明文档

## ⚠️ 重要警告
**本目录中的所有脚本已被弃用，不建议在生产环境中使用。**

## 弃用原因

### 数据质量问题
1. **缺乏真实约束**：生成的数据不能体现真实排课场景的复杂约束关系
2. **随机性过强**：时间安排、教师分配过于随机，不符合教学规律
3. **约束不一致**：生成的数据可能包含大量约束冲突，影响算法验证效果

### 技术架构问题
1. **脚本冗余**：存在大量功能重复的数据生成脚本
2. **缺乏标准化**：没有统一的数据生成接口和规范
3. **维护困难**：代码分散，难以统一优化和维护

### 算法验证不足
1. **无法体现算法优势**：生成的数据不能充分展示智能排课算法的优化能力
2. **缺乏场景覆盖**：没有针对性的约束场景测试数据
3. **结果验证困难**：缺乏课程表合理性的可视化验证

## 目录结构

```
deprecated_scripts/
├── legacy_generators/          # 旧数据生成脚本
│   ├── generate_real_million_data.py
│   ├── generate_real_million_data_simplified.py
│   ├── professional_million_generator.py
│   ├── enhanced_million_generator.py
│   ├── fixed_million_generator.py
│   ├── efficient_million_generator.py
│   └── ultra_simple_million.py
├── legacy_importers/           # 旧数据导入脚本
│   ├── import_mega_data.py
│   ├── import_enhanced_mega_data.py
│   ├── import_generated_data.py
│   ├── docker_import_mega_data.py
│   ├── streaming_import.py
│   ├── simple_mega_import.py
│   └── medium_import.py
├── legacy_validators/          # 旧数据验证脚本
│   ├── data_validation_report.py
│   ├── data_verification.py
│   ├── verify_import_results.py
│   ├── final_verification.py
│   └── final_verification_report.py
└── DEPRECATED_NOTICE.md       # 本说明文档
```

## 替代方案

推荐使用新的智能数据生成系统：

1. **智能场景生成器**：基于真实教学场景建模的数据生成器
2. **约束感知生成器**：考虑课程依赖、教师资质、时间合理性的数据生成
3. **算法验证框架**：专门为验证排课算法设计的测试数据集
4. **可视化验证工具**：提供课程表合理性的直观验证

## 保留原因

这些脚本被保留而非删除，原因如下：

1. **历史参考**：作为项目发展历史的记录
2. **代码复用**：部分功能模块可能在新系统中复用
3. **学习参考**：为了解项目演进过程提供参考
4. **安全备份**：避免意外删除重要功能

## 使用建议

如果确实需要使用这些脚本：

1. **仅用于测试**：不要在生产环境使用
2. **谨慎运行**：这些脚本可能包含已知的Bug
3. **数据验证**：使用前务必验证生成数据的质量
4. **及时迁移**：尽快迁移到新的数据生成系统

---

**生成时间**：2025年8月31日
**状态**：已弃用
**建议**：使用新的智能数据生成系统