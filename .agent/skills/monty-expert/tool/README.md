# Monty Executor Tool

Secure Python code execution using Monty (Rust-based interpreter for AI)

## Installation

```bash
pip install pydantic-monty --break-system-packages
```

## Usage Examples

### Basic Execution

```bash
# Simple calculation
python3 agent_client.py --code 'result = sum(range(10)); result'

# With print statements
python3 agent_client.py --code 'print("Hello World!"); 42'

# Multiple lines
python3 agent_client.py --code 'def fib(n): return n if n<=1 else fib(n-1)+fib(n-2); fib(10)'
```

### With Input Variables

**Important**: In Monty, input variables are declared at the top of the code:

```bash
# Declare inputs first, then use them
python3 agent_client.py --code 'x, y = inputs["x"], inputs["y"]; x + y' --inputs '{"x": 10, "y": 20}'
```

Or use the simplified approach:

```bash
python3 agent_client.py --code 'x = 10; y = 20; print(f"x + y = {x + y}")'
```

### Complex Examples

```python
# Data processing
python3 agent_client.py --code '
data = [1, 2, 3, 4, 5]
total = sum(data)
average = total / len(data)
print(f"Total: {total}, Average: {average}")
average
'

# Sorting algorithm
python3 agent_client.py --code '
def quicksort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

quicksort([3,6,8,10,1,2,1])
'

# String manipulation
python3 agent_client.py --code '
text = "Hello World"
result = text.lower().replace(" ", "_")
print(result)
result
'
```

### External Functions

To call host functions from Monty:

```python
# On host side
def fetch_data(url):
    # Implementation
    return data

# Expose to Monty
python3 agent_client.py --code 'data = fetch_data("https://api.example.com"); process(data)' --functions fetch_data
```

## Output Format

The tool returns JSON:

```json
{
  "status": "success",
  "output": "<result of last expression>"
}
```

Or on error:

```json
{
  "status": "error",
  "error": "<error type>",
  "details": "<error message>"
}
```

## Security Features

- ✅ No filesystem access
- ✅ No network access (unless via external functions)
- ✅ No environment variable access
- ✅ Strict memory limits
- ✅ Timeout protection
- ✅ Startup in ~0.06ms

## Limitations

- ❌ No Python standard library (except select modules)
- ❌ No third-party libraries
- ❌ No class definitions (support coming soon)
- ❌ No match statements (support coming soon)

## Best Practices

1. **Keep code simple** - Monty is designed for AI-generated code snippets
2. **Use external functions** for complex operations (network, file I/O)
3. **Set timeouts** to prevent infinite loops
4. **Test inputs** before execution
5. **Avoid side effects** - Monty is not for persistent state
