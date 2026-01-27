---
name: tool-development-expert
version: 2026.01.23
description: Meta-skill for standardizing AI creation of new skills and tools. Enforces strict validation and naming.
---

# Tool Development Expert

Meta-protocol for creating new Agent Skills/Tools.

## 1. Naming & Structure (STRICT)

- **Skill**: `.agent/skills/{name}-expert/SKILL.md` (Regex: `^[a-z0-9-]+-expert$`)
- **Tool**: `tools/{name}-tool/` (Regex: `^[a-z0-9-]+-tool$`)
- **Entry**: `tools/{name}-tool/agent_client.py` (Must exist)

## 2. Validation Checklist (Auto-Verify)

Run these checks after creation:

1.  `test -f .agent/skills/{name}-expert/SKILL.md`
2.  `test -f tools/{name}-tool/agent_client.py`
3.  `grep -q "{name}-expert" AGENTS.md` (Update mapping table)

## 3. Templates

### 3.1 SKILL.md Template

```markdown
---
name: {name}-expert
description: {description}
status: active
type: execution
---

# {Name} Expert

## Agent Instructions

### CLI Constraints

- Rule 1

### Commands

- `cmd`: Description
```

### 3.2 agent_client.py Template

```python
import sys, subprocess, os
TOOL_SCRIPT = os.path.join(os.path.dirname(__file__), "main.py")

def run_tool(**kwargs):
    cmd = [sys.executable, TOOL_SCRIPT]
    # ... args building ...
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    # Parse argv[1] or build args
    print(run_tool())
```
