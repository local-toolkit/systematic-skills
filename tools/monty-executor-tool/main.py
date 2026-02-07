#!/usr/bin/env python3
"""
Monty Executor Main - Secure Python code execution using pydantic-monty
"""

import sys
import json
import argparse

try:
    import pydantic_monty
except ImportError:
    print(json.dumps({
        "error": "pydantic-monty not installed",
        "fix": "pip install pydantic-monty --break-system-packages"
    }), file=sys.stderr)
    sys.exit(1)


def execute_code(code, inputs=None, external_functions=None, 
               script_name="script.py", type_check=False):
    """
    Execute Python code using Monty
    
    Args:
        code: Python code string
        inputs: Dict of input variables
        external_functions: List of external function names
        script_name: Name for the script (for error messages)
        type_check: Whether to run type checking
        
    Returns:
        Execution result dict with 'output' or 'error'
    """
    try:
        # Prepare input list
        input_list = list(inputs.keys()) if inputs else []
        
        # Prepare external functions list
        func_list = list(external_functions) if external_functions else []
        
        # Create Monty instance
        if input_list:
            m = pydantic_monty.Monty(
                code,
                inputs=input_list,
                external_functions=func_list,
                script_name=script_name,
                type_check=type_check
            )
            # Execute with inputs
            result = m.run(inputs=inputs)
        else:
            m = pydantic_monty.Monty(
                code,
                external_functions=func_list,
                script_name=script_name,
                type_check=type_check
            )
            # Execute without inputs
            result = m.run()
        
        # Convert Monty output to JSON-serializable format
        return {
            "status": "success",
            "output": str(result)
        }
    
    except pydantic_monty.MontyRuntimeError as e:
        return {
            "status": "error",
            "error": "Runtime error",
            "details": str(e)
        }
    except pydantic_monty.MontySyntaxError as e:
        return {
            "status": "error",
            "error": "Syntax error",
            "details": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {type(e).__name__}",
            "details": str(e)
        }


def execute_from_file(file_path, inputs=None):
    """
    Execute Python code from a file using Monty
    
    Args:
        file_path: Path to Python file
        inputs: Dict of input variables
        
    Returns:
        Execution result dict
    """
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        script_name = os.path.basename(file_path)
        return execute_code(code, inputs=inputs, script_name=script_name)
    
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "File not found",
            "details": file_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to read file: {type(e).__name__}",
            "details": str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description="Monty Executor - Secure Python code sandbox",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Execution source
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--code", help="Python code to execute")
    group.add_argument("--file", help="Python file to execute")
    
    # Options
    parser.add_argument("--inputs", help="Inputs as JSON string")
    parser.add_argument("--functions", help="Comma-separated external function names")
    parser.add_argument("--timeout", type=int, default=30, 
                      help="Execution timeout in seconds")
    parser.add_argument("--memory", type=int, default=128,
                      help="Memory limit in MB (informational)")
    parser.add_argument("--input-type", help="Input data type hint")
    parser.add_argument("--script-name", default="script.py",
                      help="Script name for error messages")
    
    args = parser.parse_args()
    
    # Parse inputs
    inputs = None
    if args.inputs:
        try:
            inputs = json.loads(args.inputs)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "status": "error",
                "error": "Invalid JSON in --inputs",
                "details": str(e)
            }), file=sys.stderr)
            sys.exit(1)
    
    # Parse external functions
    external_functions = None
    if args.functions:
        external_functions = [f.strip() for f in args.functions.split(',')]
    
    # Execute
    if args.file:
        # Import os for file handling
        import os
        result = execute_from_file(args.file, inputs=inputs)
    else:
        result = execute_code(
            args.code,
            inputs=inputs,
            external_functions=external_functions,
            script_name=args.script_name,
            type_check=False
        )
    
    # Output result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
