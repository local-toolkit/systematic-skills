#!/usr/bin/env python3
"""
Monty Auto-Integration Tool

Automatically integrates execution skills into Monty external functions.
"""

import sys
import os
import subprocess
import json
import argparse
from pathlib import Path
from typing import List, Dict


class MontyAutoIntegrator:
    """Monty 自动化集成器"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.registry_path = root_dir / ".agent/skill_registry.json"
        self.external_funcs_path = (
            root_dir / ".agent/skills/monty-expert/tool/external_functions.py"
        )
        self.integrated_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    def load_registry(self) -> List[Dict]:
        """加载技能注册表"""
        if not self.registry_path.exists():
            print(f"❌ Registry not found: {self.registry_path}")
            return []

        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_unintegrated_skills(self, registry: List[Dict]) -> List[Dict]:
        """获取未集成的技能"""
        unintegrated = []
        exempt_skills = {
            "anthropics-skills-expert",
            "frontend-design-expert",
            "literature-search-expert",
            "mcp-builder-expert",
            "tool-development-expert",
            "vtt-recitation-expert",
        }

        for skill in registry:
            # 豁免：meta 类型
            if skill.get("type") == "meta":
                continue
            # 豁免：在豁免列表中
            if skill.get("name") in exempt_skills:
                continue
            # 跳过：已集成
            if skill.get("monty_integrated", False):
                continue
            # 跳过：没有 tool 目录
            if not skill.get("tool_dir"):
                continue

            unintegrated.append(skill)

        return unintegrated

    def integrate_skill(self, skill: Dict, verbose: bool = True) -> Dict:
        """集成单个技能"""
        skill_name = skill["name"]

        if verbose:
            print(f"\n📦 Integrating: {skill_name}")

        cmd = [
            sys.executable,
            "scripts/integrate_skill_to_monty.py",
            skill_name,
            "--auto",
            "--verify",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120, cwd=self.root_dir
            )

            if result.returncode == 0:
                if verbose:
                    print(f"  ✅ Success")

                # 更新注册表
                skill["monty_integrated"] = True

                # 解析函数数量（从输出中提取）
                # 简单计数：搜索 "@register_external_function"
                lines = result.stdout.split("\n")
                func_count = sum(
                    1 for line in lines if "@register_external_function" in line
                )
                skill["monty_functions_count"] = func_count

                self.integrated_count += 1
                return {"success": True, "functions_count": func_count}
            else:
                if verbose:
                    print(f"  ❌ Failed: {result.stderr[:200]}")

                self.failed_count += 1
                return {"success": False, "error": result.stderr[:200]}

        except subprocess.TimeoutExpired:
            if verbose:
                print(f"  ⏱️  Timeout")

            self.failed_count += 1
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            if verbose:
                print(f"  ⚠️  Exception: {e}")

            self.failed_count += 1
            return {"success": False, "error": str(e)}

    def integrate_all(self, incremental: bool = False, verbose: bool = True) -> Dict:
        """批量集成所有技能"""

        registry = self.load_registry()

        if incremental:
            skills = self.get_unintegrated_skills(registry)
            mode_str = "Incremental"
        else:
            skills = [s for s in registry if s.get("type") == "execution"]
            mode_str = "Full"

        results = {
            "total": len(skills),
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }

        print(f"\n{'=' * 60}")
        print(f"🤖 Monty Auto-Integration ({mode_str})")
        print(f"{'=' * 60}")
        print(f"\n📊 Skills to integrate: {len(skills)}")

        for i, skill in enumerate(skills, 1):
            if verbose:
                print(f"\n[{i}/{len(skills)}] {skill['name']}")

            result = self.integrate_skill(skill, verbose=verbose)

            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1

        # 保存更新后的注册表
        if not args.dry_run:
            self.save_registry(registry)

        return results

    def save_registry(self, registry: List[Dict]) -> None:
        """保存更新后的注册表"""
        try:
            # 创建 .agent 目录如果需要
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存 with pretty 格式
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Registry saved to: {self.registry_path}")
            print(f"📊 Total skills: {len(registry)}")
        except Exception as e:
            print(f"❌ Failed to save registry: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-integrate skills to Monty",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--incremental",
        "-i",
        action="store_true",
        help="Only integrate new skills (skip already integrated)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-integration of all execution skills",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress output except errors"
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    root_dir = Path.cwd()
    integrator = MontyAutoIntegrator(root_dir)

    if args.force:
        results = integrator.integrate_all(incremental=False, verbose=not args.quiet)
    else:
        results = integrator.integrate_all(
            incremental=args.incremental, verbose=not args.quiet
        )

    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 Integration Summary")
    print(f"{'=' * 60}")
    print(f"  Total:    {results['total']}")
    print(f"  ✅ Success: {results['success']}")
    print(f"  ❌ Failed: {results['failed']}")
    print(f"  ⏭️ Skipped: {results['skipped']}")

    # Exit code based on results
    if results["failed"] == 0:
        print("\n✨ All integrations completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {results['failed']} integration(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
