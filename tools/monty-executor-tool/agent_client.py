#!/usr/bin/env python3
"""
Monty Executor - Secure Python code execution using Monty (Rust-based interpreter)
Agent client for Clawdbot integration
"""

import sys
import os
import subprocess
import json
import argparse

TOOL_SCRIPT = os.path.join(os.path.dirname(__file__), "main.py")

def run_monty(code=None, file=None, inputs=None, functions=None, timeout=30, memory=128, input_type=None):
    """
    Execute Python code using Monty interpreter
    
    Args:
        code: Python code string to execute
        file: Path to Python file to execute
        inputs: JSON string or dict of inputs for the code
        functions: Comma-separated list of external function names to expose
        timeout: Execution timeout in seconds (default: 30)
        memory: Memory limit in MB (default: 128)
        input_type: Type of input data (json, text, etc.)
    """
    cmd = [sys.executable, TOOL_SCRIPT]
    
    if code:
        cmd.extend(["--code", code])
    elif file:
        cmd.extend(["--file", file])
    else:
        return {"error": "Either --code or --file must be specified"}
    
    if inputs:
        if isinstance(inputs, dict):
            inputs = json.dumps(inputs)
        cmd.extend(["--inputs", inputs])
    
    if functions:
        cmd.extend(["--functions", functions])
    
    cmd.extend(["--timeout", str(timeout)])
    cmd.extend(["--memory", str(memory)])
    
    if input_type:
        cmd.extend(["--input-type", input_type])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5  # Add buffer for Monty overhead
        )
        
        if result.returncode != 0:
            return {
                "error": "Monty execution failed",
                "exit_code": result.returncode,
                "stderr": result.stderr
            }
        
        # Try to parse output as JSON
        try:
            output = json.loads(result.stdout)
            return output
        except json.JSONDecodeError:
            return {"output": result.stdout}
    
    except subprocess.TimeoutExpired:
        return {"error": "Execution timeout"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Monty Executor - Safe Python code sandbox")
    parser.add_argument("--code", help="Python code to execute")
    parser.add_argument("--file", help="Python file to execute")
    parser.add_argument("--inputs", help="Inputs as JSON string")
    parser.add_argument("--functions", help="Comma-separated external function names")
    parser.add_argument("--timeout", type=int, default=30, help="Execution timeout (seconds)")
    parser.add_argument("--memory", type=int, default=128, help="Memory limit (MB)")
    parser.add_argument("--input-type", help="Input data type")
    
    args = parser.parse_args()
    
    inputs = args.inputs
    if inputs:
        try:
            inputs = json.loads(inputs)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in --inputs"}
    
    result = run_monty(
        code=args.code,
        file=args.file,
        inputs=inputs,
        functions=args.functions,
        timeout=args.timeout,
        memory=args.memory,
        input_type=args.input_type
    )
    
    if "error" in result:
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
