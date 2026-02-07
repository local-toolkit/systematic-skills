#!/usr/bin/env python3
"""
Integrate a skill into Monty external functions
Usage: python integrate_skill_to_monty.py <skill-name> [--verify] [--auto]
"""

import sys
import os
import subprocess
import datetime
import shutil
from pathlib import Path


def check_skill_exists(skill_name: str) -> bool:
    """Check if skill directory exists."""
    skill_path = Path(f".agent/skills/{skill_name}")

    if not skill_path.exists():
        print(f"[ERROR] Skill directory not found: .agent/skills/{skill_name}")
        return False

    # Check for tool directory
    tool_dir = skill_path / "tool"
    if not tool_dir.exists():
        print(f"[WARN] Tool directory not found: {tool_dir}")
        print(f"        This might be a meta-skill (not requiring integration)")
        return False

    return True


def check_already_integrated(skill_name: str) -> bool:
    """Check if skill is already integrated to Monty."""
    external_funcs_path = Path(f".agent/skills/monty-expert/tool/external_functions.py")

    if not external_funcs_path.exists():
        return False

    content = external_funcs_path.read_text()
    base_name = skill_name.replace("-expert", "")

    # Check for any function with this base name
    patterns = [
        f'@register_external_function("{base_name}_',
        f"# === {base_name.replace('-', ' ').title()} Functions ===",
    ]

    return any(pattern in content for pattern in patterns)


def backup_external_functions() -> Path:
    """Create backup of external_functions.py before modification."""
    src = Path(f".agent/skills/monty-expert/tool/external_functions.py")
    backup_dir = src.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"external_functions_{timestamp}.py"

    shutil.copy2(src, backup_path)
    print(f"    💾 Backup: {backup_path.name}")

    return backup_path


def restore_backup(backup_path: Path) -> bool:
    """Restore from backup if integration fails."""
    target = backup_path.parent / "external_functions.py"

    try:
        shutil.copy2(backup_path, target)
        print(f"    🔄 Restored from backup")
        return True
    except Exception as e:
        print(f"    ❌ Restore failed: {e}")
        return False


def validate_external_functions_syntax() -> bool:
    """Validate Python syntax of external_functions.py."""
    try:
        import ast

        external_funcs_path = Path(
            f".agent/skills/monty-expert/tool/external_functions.py"
        )
        with open(external_funcs_path, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        print("    ✅ Syntax valid")
        return True
    except SyntaxError as e:
        print(f"    ❌ Syntax error at line {e.lineno}: {e.msg}")
        print(
            f"        {e.text.split('\\n')[e.lineno - 1 : e.lineno + 1] if e.text else ''}"
        )
        return False
    except Exception as e:
        print(f"    ❌ Exception validating: {e}")
        return False


def generate_wrapper(skill_name: str) -> tuple[bool, str]:
    """Generate wrapper code for skill."""
    print(f"[+] Generating wrapper for {skill_name}...")

    # Detect if MCP tool
    mcp_server_path = Path(f".agent/skills/{skill_name}/tool/mcp_server.py")
    is_mcp = mcp_server_path.exists()

    # Build command
    cmd = [sys.executable, "scripts/generate_monty_wrapper.py", skill_name]
    if is_mcp:
        cmd.append("--mcp")

    # Execute wrapper generation
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Failed to generate wrapper")
        print(f"        Error: {result.stderr}")
        return False, ""

    # Extract only function code (skip print statements)
    lines = result.stdout.split("\n")
    func_lines = []
    in_wrapper_code = False
    for line in lines:
        # Look for "=== {skill_name.title()} Functions ===" marker
        if f"=== {skill_name.replace('-', ' ').title()} Functions ===" in line:
            in_wrapper_code = True

        # Only collect lines after marker
        if in_wrapper_code:
            func_lines.append(line)

    wrapper_code = "\n".join(func_lines)
    return True, wrapper_code


def append_to_external_functions(wrapper_code: str, skill_name: str) -> bool:
    """Append wrapper code to external_functions.py."""
    external_funcs_path = Path(f".agent/skills/monty-expert/tool/external_functions.py")

    if not external_funcs_path.exists():
        print(f"[ERROR] external_functions.py not found: {external_funcs_path}")
        return False

    print(f"[+] Appending to external_functions.py...")

    # Read existing content
    with open(external_funcs_path, "r", encoding="utf-8") as f:
        existing_content = f.read()

    # Find insertion point (before Registry Access Functions section)
    insertion_marker = "# === Registry Access Functions ==="

    if insertion_marker not in existing_content:
        print(f"[WARN] Insertion marker not found, appending to end")
        new_content = existing_content + "\n\n" + wrapper_code
    else:
        # Insert before marker
        parts = existing_content.split(insertion_marker)
        new_content = parts[0] + wrapper_code + "\n\n" + insertion_marker + parts[1]

    # Write back
    with open(external_funcs_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[OK] Wrapper appended successfully")
    return True


def verify_integration(skill_name: str) -> bool:
    """Verify that integration works."""
    print(f"[?] Verifying integration...")

    # Test 1: List external functions
    print("   Testing: --list-external-funcs")
    result = subprocess.run(
        [sys.executable, ".agent/skills/monty-expert/tool/external_functions.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        print(f"[WARN] external_functions.py has syntax errors")
        print(f"   Error: {result.stderr}")
        return False

    # Test 2: Check if new functions appear
    base_name = skill_name.replace("-expert", "")
    if base_name in result.stdout:
        print(f"   [OK] Function {base_name} found in list")
        return True
    else:
        print(f"   [WARN] Function {base_name} not found in output")
        return False


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python integrate_skill_to_monty.py <skill-name> [--verify] [--auto]"
        )
        print("")
        print("Examples:")
        print("  python integrate_skill_to_monty.py playwright-expert")
        print("  python integrate_skill_to_monty.py paper-audit-expert --verify")
        print("  python integrate_skill_to_monty.py news-aggregator-expert --auto")
        sys.exit(1)

    skill_name = sys.argv[1]
    should_verify = "--verify" in sys.argv
    auto_mode = "--auto" in sys.argv

    # NEW: Auto mode - suppress most output for cleaner logs
    if auto_mode:
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    # NEW: In auto mode, perform backup first
    backup_path = None
    if auto_mode:
        backup_path = backup_external_functions()

    # Step 1: Check skill exists
    if not check_skill_exists(skill_name):
        if not auto_mode:
            print(
                f"[ERROR] Cannot integrate {skill_name}: skill not found or has no tool"
            )
            sys.exit(1)
        return {"success": False, "error": "Skill not found"}

    # NEW: Check if already integrated
    if auto_mode and check_already_integrated(skill_name):
        print(f"[INFO] {skill_name} already integrated, skipping")
        if auto_mode:
            sys.stdout.close()
            sys.stdout = original_stdout
        return {"success": True, "already_integrated": True}

    # Step 2: Generate wrapper
    success, wrapper_code = generate_wrapper(skill_name)
    if not success:
        if not auto_mode:
            print(f"[ERROR] Integration failed for {skill_name}")
            sys.exit(1)
        return {"success": False, "error": "Wrapper generation failed"}

    # Step 3: Append to external_functions.py
    if not append_to_external_functions(wrapper_code, skill_name):
        if not auto_mode:
            print(f"[ERROR] Integration failed for {skill_name}")
            if auto_mode and backup_path:
                restore_backup(backup_path)
            sys.exit(1)
        return {"success": False, "error": "Failed to append to external_functions.py"}

    # NEW: Validate syntax after integration
    if auto_mode:
        if not validate_external_functions_syntax():
            if backup_path:
                restore_backup(backup_path)
            return {"success": False, "error": "Syntax validation failed"}

    # Step 4: Verify (if requested)
    if should_verify or auto_mode:
        if not verify_integration(skill_name):
            if not auto_mode:
                print(f"[WARN] Integration completed but verification failed")
            else:
                print(f"[OK] Integration and verification successful for {skill_name}")
        else:
            if not auto_mode:
                print(f"[OK] Integration successful for {skill_name}")
                print(
                    f"[INFO] Run with --verify to test: python integrate_skill_to_monty.py {skill_name} --verify"
                )

    # Restore stdout in auto mode
    if auto_mode:
        sys.stdout.close()
        sys.stdout = original_stdout


if __name__ == "__main__":
    main()
