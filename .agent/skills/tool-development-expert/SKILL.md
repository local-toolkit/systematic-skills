---
name: tool-development-expert
version: 2026.01.23
description: Meta-skill for standardizing AI creation of new skills and tools. Enforces all rules from AGENT_INSTRUCTIONS.md with mandatory validation checks.
---

# Tool Development Expert (Meta-Protocol)

This skill serves as a meta-protocol for creating new skills and tools within the AI Agent toolset ecosystem. It enforces strict adherence to the architecture and standards defined in `AGENT_INSTRUCTIONS.md`.

## 1. Mandatory Pre-conditions

Before creating ANY new skill or tool, the agent MUST:
- Read and understand `/mnt/c/Users/xujin/workspace/Tools/AGENT_INSTRUCTIONS.md`
- Verify the proposed functionality doesn't conflict with existing skills
- Confirm the naming follows conventions: `{function-name}-expert` and `{function-name}-tool`

## 2. Creation Protocol - Skills

### 2.1 Skill File Structure
The new `SKILL.md` MUST contain:
- Frontmatter with `name`, `version`, and `description`
- Clear section structure with numbered headings
- Specific protocols for the domain expertise
- Error handling strategies
- Usage examples or templates

### 2.2 Skill Content Standards
- Provide expert-level knowledge for the domain
- Include specific operation protocols
- Define input/output specifications
- Establish constraints and validation rules

## 3. Creation Protocol - Tools

### 3.1 Tool Directory Structure
Each tool directory MUST contain:
- `agent_client.py` - Mandatory execution entry point
- `main.py` - Core implementation logic
- `requirements.txt` - Python dependencies
- `venv/` - Virtual environment (optional but recommended)

### 3.2 agent_client.py Interface Standards
The `agent_client.py` MUST:
- Accept user request as command-line argument
- Follow execution format: `python {tool}/agent_client.py "<request>"`
- Return execution results and error information
- Implement proper error handling and logging

## 4. Mandatory Validation Checklist (Auto-Verification)

The agent MUST automatically execute this verification process after creating any new skill or tool:

### 4.1 Skill Auto-Verification
- [ ] File exists at `.agent/skills/{function-name}-expert/SKILL.md`
- [ ] Contains proper frontmatter (name, version, description)
- [ ] Follows naming convention: `{function-name}-expert`
- [ ] Includes clear domain protocols and constraints
- [ ] Provides usage examples

**Verification Command:**
```bash
test -f .agent/skills/{function-name}-expert/SKILL.md && grep -q "^name:" .agent/skills/{function-name}-expert/SKILL.md
```

### 4.2 Tool Auto-Verification
- [ ] Directory exists at `{function-name}-tool/`
- [ ] Contains `agent_client.py` as execution entry
- [ ] Follows naming convention: `{function-name}-tool`
- [ ] Implements proper command-line interface
- [ ] Handles errors and provides meaningful feedback

**Verification Commands:**
```bash
test -d {function-name}-tool
test -f {function-name}-tool/agent_client.py
test -f {function-name}-tool/main.py
test -f {function-name}-tool/requirements.txt
```

### 4.3 Documentation Auto-Verification
- [ ] Updated `AGENT_INSTRUCTIONS.md` mapping table
- [ ] Added entry with correct status (Active/Pending Implementation)
- [ ] Included description and tool directory

**Verification Command:**
```bash
grep -q "{function-name}-expert" AGENT_INSTRUCTIONS.md
```

## 5. Naming Convention Enforcement

STRICT adherence to:
- **Skill names**: `{function-name}-expert`
- **Tool directories**: `{function-name}-tool`
- **No deviations allowed**: This ensures consistency across the ecosystem

**Naming Pattern Regex:** `^[a-z0-9-]+-expert$` for skills, `^[a-z0-9-]+-tool$` for directories

## 6. Conflict Prevention

Before creating new skills, automatically check:
1. List existing skills in `.agent/skills/`
2. Verify no functionality overlap
3. Ensure unique naming
4. Validate against existing tools in root directory

**Conflict Check Command:**
```bash
ls -1 .agent/skills/ | grep -v "^tool-development-expert$"
ls -1d *-tool/ | grep -v "yt-dlp-tool/"
```

## 7. Quality Assurance

The new skill/tool MUST:
- Follow existing skill formatting (refer to `yt-dlp-expert` or `literature-search-expert`)
- Adhere to tool implementation patterns (refer to `yt-dlp-tool/agent_client.py`)
- Maintain consistency with project architecture
- Include proper error handling and user feedback

## 8. Update Workflow

After successful creation and verification:
1. Update `/mnt/c/Users/xujin/workspace/Tools/AGENT_INSTRUCTIONS.md`
2. Add new entry to the mapping table (Section 3)
3. Set status to "Active" or "Pending Implementation" based on implementation status
4. Test the complete workflow if tool is implemented

## 9. Templates for AI Usage

### 9.1 SKILL.md Template
Copy this template and customize for new skills:

```markdown
---
name: {function-name}-expert
version: 2026.01.23
description: Brief description of what this skill does and its expertise domain
---

# {Function Name} Expert

Expert knowledge base for {function domain} operations.

## 1. Core Protocols

### 1.1 Pre-conditions
- List required environment states
- Specify dependencies
- Define version requirements

### 1.2 Operation Constraints
- Mandatory rules for execution
- Parameter dependencies
- Security considerations

## 2. Operation Sets

### 2.1 Primary Operations
- **Operation 1**: Description and template
- **Operation 2**: Description and template

## 3. Error Handling
- Error code 1: Solution
- Error code 2: Solution

## 4. Usage Examples
"Example of how to request this skill's functionality"
```

### 9.2 agent_client.py Template
Copy this template and customize for new tools:

```python
import sys
import subprocess
import os

# Configuration
TOOL_SCRIPT = os.path.join(os.path.dirname(__file__), "main.py")

def execute_tool(**kwargs):
    """Executes the tool with the given arguments."""
    # Find venv python if available
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, "venv", "bin", "python")

    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable

    # Build command
    cmd = [python_exe, TOOL_SCRIPT]

    # Add arguments (customize based on your tool's needs)
    if kwargs.get('param1'):
        cmd.extend(['--param1', kwargs['param1']])

    # Execute
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"SUCCESS:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR (Exit Code {e.returncode}):\n{e.stderr}\n{e.stdout}"
    except Exception as e:
        return f"EXECUTION FAILED: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_client.py \"<your request>\"")
        sys.exit(1)

    request = sys.argv[1]
    # Parse request and call execute_tool with appropriate parameters
    # This is where you implement the logic to convert natural language to tool parameters
    result = execute_tool()  # Add appropriate parameters
    print(result)
```

## 10. Complete Development Workflow

When creating a new skill/tool:

1. **Phase 1: Planning**
   - Read AGENT_INSTRUCTIONS.md
   - Check for conflicts
   - Verify naming convention

2. **Phase 2: Skill Creation**
   - Create `.agent/skills/{function-name}-expert/SKILL.md`
   - Use the SKILL.md template
   - Include domain expertise and protocols

3. **Phase 3: Tool Creation**
   - Create `{function-name}/` directory
   - Implement `agent_client.py` (use template)
   - Implement `main.py` with core logic
   - Create `requirements.txt`

4. **Phase 4: Validation**
   - Run auto-verification commands
   - Complete validation checklist
   - Fix any issues found

5. **Phase 5: Documentation**
   - Update `AGENT_INSTRUCTIONS.md` mapping table
   - Set correct status (Active/Pending Implementation)
   - Test if implemented

## 11. Status Marking Rules

Use these status values in the AGENT_INSTRUCTIONS.md mapping table:
- **Active**: Both skill and tool are fully implemented and tested
- **Pending Implementation**: Skill exists, tool implementation is incomplete
- **Pending**: Both skill and tool are in development

**Status Selection Logic:**
- If both SKILL.md and agent_client.py exist → "Active"
- If only SKILL.md exists → "Pending Implementation"
- If neither exists (during creation) → "Pending"