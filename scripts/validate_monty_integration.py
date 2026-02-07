#!/usr/bin/env python3
"""
Validate Monty Integration Script

Checks for:
1. external_functions.py syntax
2. All skills properly integrated
3. No duplicate functions
4. Function signatures valid
5. Documentation complete
"""

import ast
import sys
import json
import re
from pathlib import Path
from typing import List, Dict


def validate_syntax(file_path: Path) -> bool:
    """验证 Python 语法"""
    print("\n[CHECK] Python syntax validation")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        print("  ✅ Syntax valid")
        return True
    except SyntaxError as e:
        print(f"  ❌ Syntax error at line {e.lineno}: {e.msg}")
        return False


def validate_no_duplicates(file_path: Path) -> bool:
    """检查重复函数名"""
    print("\n[CHECK] Duplicate function names")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'@register_external_function\("([^"]+)"\)'
    matches = re.findall(pattern, content)

    duplicates = [name for name in set(matches) if matches.count(name) > 1]

    if duplicates:
        print(f"  ❌ Duplicate functions: {duplicates}")
        for dup in duplicates:
            count = matches.count(dup)
            print(f"     - {dup} ({count} times)")
        return False
    else:
        print(f"  ✅ No duplicates ({len(matches)} functions)")
        return True


def validate_documentation(file_path: Path) -> bool:
    """验证函数文档"""
    print("\n[CHECK] Function documentation")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取函数定义和文档字符串
    pattern = r'@register_external_function\("([^"]+)"\)\s*def\s+\w+\([^)]*\)\s*->\s*[^:]+:\s+"""'
    matches = re.findall(pattern, content)

    undocumented = []
    for match in matches:
        func_name = match[0]
        docstring = match[1].strip()

        if len(docstring) < 20:
            undocumented.append(func_name)
        elif not docstring.startswith('"""'):
            undocumented.append(func_name)

    if undocumented:
        print(f"  ⚠️  Incomplete documentation: {len(undocumented)} functions")
        for func in undocumented[:5]:
            print(f"     - {func}")
        return False
    else:
        print(f"  ✅ All functions documented ({len(matches)} functions)")
        return True


def validate_skill_coverage() -> bool:
    """验证技能集成覆盖率"""
    print("\n[CHECK] Skill integration coverage")

    # 加载注册表
    registry_path = Path(__file__).parent.parent / ".agent/skill_registry.json"

    if not registry_path.exists():
        print(f"  ❌ Registry not found: {registry_path}")
        return False

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # 加载外部函数
    try:
        from .agent.skills.monty_expert.tool.external_functions import (
            EXTERNAL_FUNCTIONS,
        )

        registered_funcs = set(EXTERNAL_FUNCTIONS.keys())
    except ImportError:
        print("  ⚠️  Could not load external functions for validation")
        registered_funcs = set()

    # 豁免列表
    exempt_skills = {
        "anthropics-skills-expert",
        "frontend-design-expert",
        "literature-search-expert",
        "mcp-builder-expert",
        "tool-development-expert",
        "vtt-recitation-expert",
    }

    # 筛选需要集成的技能
    required_skills = [
        s
        for s in registry
        if s.get("type") == "execution" and s["name"] not in exempt_skills
    ]

    # 检查哪些技能已集成
    missing = []
    for skill in required_skills:
        skill_name = skill["name"].replace("-expert", "")

        # 检查是否任何外部函数以 skill_name 开头
        skill_prefix = skill_name.replace("-expert", "")
        skill_integrated = any(
            func_name.startswith(skill_prefix) for func_name in registered_funcs
        )

        if not skill_integrated:
            missing.append(skill["name"])

    if missing:
        print(f"  ⚠️  Missing integration: {len(missing)} skills")
        for skill in missing[:10]:
            print(f"     - {skill}")
        if len(missing) > 10:
            print(f"     ... and {len(missing) - 10} more")
        return False
    else:
        print(f"  ✅ All {len(required_skills)} execution skills integrated")
        return True


def main():
    """主验证函数"""
    print("=" * 60)
    print("🔍 Monty Integration Validation")
    print("=" * 60)

    external_funcs_path = (
        Path(__file__).parent.parent
        / ".agent/skills/monty-expert/tool/external_functions.py"
    )

    if not external_funcs_path.exists():
        print(f"❌ File not found: {external_funcs_path}")
        sys.exit(1)

    # 运行所有验证
    results = {
        "syntax": validate_syntax(external_funcs_path),
        "no_duplicates": validate_no_duplicates(external_funcs_path),
        "documentation": validate_documentation(external_funcs_path),
        "coverage": validate_skill_coverage(),
    }

    # 汇总
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)

    all_pass = all(results.values())

    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
