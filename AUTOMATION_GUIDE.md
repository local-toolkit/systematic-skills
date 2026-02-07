# Monty 自动化集成指南

## 概述

本指南说明如何使用 Monty 自动化集成系统，将执行技能自动集成到 Monty 外部函数。

## 快速开始

### 方式 1: 自动集成（推荐）

```bash
# 1. 创建技能（如果还没创建）
python scripts/create_tool.py my-skill --type subprocess

# 2. 实现技能逻辑
# 编辑 .agent/skills/my-skill-expert/tool/main.py

# 3. 一次性完成：发现 + 集成
python scripts/discover_skills.py
```

**结果**: 
- ✅ 技能自动集成到 Monty
- ✅ 自动验证集成
- ✅ 更新注册表

### 方式 2: 批量集成

```bash
# 增量集成（只集成新技能）
python scripts/monty_auto_integration.py --incremental

# 强制全部重新集成
python scripts/monty_auto_integration.py --force

# 试运行模式（不修改）
python scripts/monty_auto_integration.py --dry-run
```

### 方式 3: 手动集成（仅在自动集成失败时使用）

```bash
# 集成特定技能
python scripts/integrate_skill_to_monty.py <skill-name> --verify

# 集成但不验证
python scripts/integrate_skill_to_monty.py <skill-name>
```

## 工作原理

### 自动集成流程

```
开发者创建/修改技能
    ↓
python scripts/discover_skills.py
    ↓
检测技能类型和集成需求
    ↓
判断：执行技能 & 未集成 & 不在豁免列表？
    ├─ Yes → 自动调用 integrate_skill_to_monty.py --auto
    │           ↓
    │       生成外部函数包装器
    │           ↓
    │       追加到 external_functions.py
    │           ↓
    │       运行验证测试
    │           ↓
    │       更新 registry (monty_integrated: true)
    │
    └─ No → 跳过（meta skill 或已集成）
        ↓
完成
```

### 检测逻辑

技能需要自动集成，如果满足以下条件：

1. ✅ 技能类型为 `execution`
2. ✅ 技能有 `tool` 目录
3. ✅ 技能不在豁免列表中
4. ✅ 技能尚未集成到 Monty

### 豁免列表

以下技能不会自动集成到 Monty：

- `anthropics-skills-expert` - Meta skill（仅提供指南）
- `frontend-design-expert` - UI only skill
- `literature-search-expert` - Documentation only skill
- `mcp-builder-expert` - Meta skill
- `tool-development-expert` - Meta skill
- `vtt-recitation-expert` - 特殊用例 skill

## 验证集成

### 检查集成状态

```bash
# 查看所有已集成技能
cat .agent/skill_registry.json | grep "monty_integrated.*true" | jq -r '.[] | select(.name, .monty_functions_count)'

# 检查特定技能
cat .agent/skill_registry.json | jq '.[] | select(.name, .monty_integrated) | select(. == "<skill-name>")'

# 列出外部函数
python .agent/skills/monty-expert/tool/main.py --list-external-funcs

# 验证集成
python scripts/validate_monty_integration.py
```

### 测试集成

```bash
# 列出函数
python .agent/skills/monty-expert/tool/main.py --list-external-funcs

# 测试新闻聚合
python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code 'news = fetch_hackernews(3); print(len(news))'

# 测试文件操作
python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code 'path = write_file("/tmp/test.txt", "hello"); print(path)'
```

# 测试工具函数
python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code 'result = convert_image("test.png", "test.jpg"); print(result)'
```

## 故障排除

### 问题：技能没有自动集成

**症状**: 运行 `python scripts/discover_skills.py` 后，技能未集成到 Monty

**诊断步骤**:

1. 检查技能类型
```bash
cat .agent/skill_registry.json | grep -A1 "<skill-name>" | grep '"type":'
```

2. 检查是否在豁免列表中
```bash
grep -i "<skill-name>" .agent/skills/tool-development-expert/SKILL.md | grep豁免
```

3. 检查是否有 tool 目录
```bash
ls -la .agent/skills/<skill-name>/tool/
```

4. 检查是否已集成
```bash
python .agent/skills/monty-expert/tool/main.py --list-external-funcs | grep "<skill-name>"
```

### 问题：自动集成失败

**症状**: `discover_scripts.py` 显示集成失败

**可能原因**:

1. **外部函数文件损坏**
   - 检查：`python -m py_compile .agent/skills/monty-expert/tool/external_functions.py`

2. **integrate 脚本错误**
   - 手动运行：`python scripts/integrate_skill_to_monty.py <skill-name> --verify`

3. **权限问题**
   - 检查：`ls -la .agent/skills/monty-expert/tool/`

4. **脚本路径错误**
   - 检查：`ls -la scripts/integrate_skill_to_monty.py`

### 解决方案

#### 方案 1: 手动集成

如果自动集成一直失败：

```bash
# 手动调用集成脚本
python scripts/integrate_skill_to_monty.py <skill-name> --verify
```

#### 方案 2: 检查脚本

```bash
# 验证脚本语法
python -m py_compile scripts/integrate_skill_to_monty.py

# 验证验证脚本语法
python -m py_compile scripts/validate_monty_integration.py

# 验证批处理脚本
python -m py_compile scripts/monty_auto_integration.py
```

#### 方案 3: 查看详细日志

```bash
# 运行发现脚本查看详细日志
python scripts/discover_skills.py 2>&1 | tee /tmp/discovery_log.txt

# 查看日志
cat /tmp/discovery_log.txt
```

#### 方案 4: 检查备份

```bash
# 查看是否有备份文件
ls -lh .agent/skills/monty-expert/tool/backups/

# 检查最近的备份
tail -1 .agent/skills/monty-expert/tool/backups/*.py
```

## 性能优化

### 加速集成

#### 增量模式

```bash
# 只集成新技能，跳过已集成的
python scripts/monty_auto_integration.py --incremental
```

#### 并发处理（高级）

```bash
# 并发处理 4 个技能
find .agent/skills -name "*-expert" -type d \
  | parallel -j 4 'python scripts/integrate_skill_to_monty.py {} --auto'
```

### 减少验证时间

```bash
# 跳过验证以加快集成
python scripts/integrate_skill_to_monty.py <skill-name> --auto --no-verify
```

## 最佳实践

### 创建新技能时

1. **遵循命名约定**
   - 函数名使用 `snake_case`
   - 返回类型注解清晰
   - 提供详细文档字符串

2. **提供完整的 CLI**
   - `--help` 显示所有选项
   - 清晰的参数说明
   - 合理的默认值

3. **错误处理**
   - 捕获所有异常
   - 提供清晰的错误消息
   - 适当的退出代码

4. **测试友好**
   - 支持 `--dry-run` 模式
   - 提供详细输出

### 集成后验证

1. **运行验证脚本**
   ```bash
   python scripts/validate_monty_integration.py
   ```

2. **测试外部函数**
   ```bash
   python .agent/skills/monty-expert/tool/main.py --list-external-funcs
   ```

3. **运行功能测试**
   ```bash
   python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code 'result = <your_func>()'
   ```

## 高级用法

### 自定义集成

对于有特殊需求的技能：

```python
# 手动编辑 external_functions.py
vi .agent/skills/monty-expert/tool/external_functions.py

# 添加自定义集成函数
```

### 批量重新集成

```bash
# 强制重新集成所有执行技能
python scripts/monty_auto_integration.py --force

# 验证并重新集成
python scripts/validate_monty_integration.py && python scripts/monty_auto_integration.py --force
```

## 命令参考

### 主要命令

| 命令 | 说明 |
|------|------|
| `python scripts/discover_skills.py` | 发现 + 自动集成 |
| `python scripts/monty_auto_integration.py` | 批量集成 |
| `python scripts/integrate_skill_to_monty.py <skill>` | 单个技能集成 |
| `python scripts/validate_monty_integration.py` | 验证集成 |
| `python .agent/skills/monty-expert/tool/main.py --list-external-funcs` | 列出函数 |
| `python .agent/skills/monty-expert/tool/main.py --code '...' | 运行 Monty 代码 |

### 高级命令

```bash
# 检查集成状态
jq -r '.[] | [.[] | select(.name, .monty_integrated)]' .agent/skill_registry.json

# 统计集成情况
jq -r '.[] | [.[] | .monty_integrated] | select(.monty_functions_count)] | add' | .agent/skill_registry.json

# 并发集成 4 个技能
find .agent/skills -name "*-expert" -type d \
  | parallel -j 4 'python scripts/integrate_skill_to_monty.py {} --auto'
```

## 附录

### A. 完整命令参考

所有可用命令的完整列表和参数说明。

### B. 错误代码参考

常见错误代码及其含义和解决方案。

### C. 配置文件参考

所有配置文件的结构和选项说明。
