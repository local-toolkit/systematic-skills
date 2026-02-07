---
description: How to test a skill's integration with Monty
---

# Testing Monty Integration

Follow these steps to verify that a new skill is correctly integrated with Monty.

## 1. Verify Adapter Existence

Check if the skill has a `monty_adapter.py` file.

```bash
ls .agent/skills/<skill-name>/tool/monty_adapter.py
```

## 2. Verify Function Registration

Run Monty's list command to ensure the skill's functions are discovered.

```bash
python .agent/skills/monty-expert/tool/main.py --list-external-funcs | grep <function_name>
```

## 3. Verify Function Execution

Run a simple Monty script calling the function.

```bash
python .agent/skills/monty-expert/tool/main.py --code '
result = <function_name>(<args>)
print(result)
' --use-external-funcs
```

## 4. Troubleshooting

If the function is not listed:

- **Check Imports**: Ensure `monty_adapter.py` imports necessary modules.
- **Check Return Type**: Ensure `get_monty_functions()` returns a dictionary of callables.
- **Debug**: Run with `python .agent/skills/monty-expert/tool/main.py --list-external-funcs` and check stderr for loading errors.
