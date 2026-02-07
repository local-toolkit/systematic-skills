#!/usr/bin/env python3
"""
Monty Executor Main - Secure Python code execution using pydantic-monty
"""

import sys
import json
import argparse
import os

try:
    import pydantic_monty
except ImportError:
    print(
        json.dumps(
            {
                "error": "pydantic-monty not installed",
                "fix": "pip install pydantic-monty --break-system-packages",
            }
        ),
        file=sys.stderr,
    )
    sys.exit(1)


def execute_code(
    code,
    inputs=None,
    external_functions=None,
    script_name="script.py",
    type_check=False,
):
    """
    Execute Python code using Monty

    Args:
        code: Python code string
        inputs: Dict of input variables
        external_functions: Dict of external function name -> callable
        script_name: Name for script (for error messages)
        type_check: Whether to run type checking

    Returns:
        Execution result dict with 'output' or 'error'
    """
    try:
        # Prepare input list
        input_list = list(inputs.keys()) if inputs else []

        # Prepare external functions
        func_list = list(external_functions.keys()) if external_functions else []
        func_dict = external_functions or {}

        # Create Monty instance
        m = pydantic_monty.Monty(
            code,
            inputs=input_list,
            external_functions=func_list,
            script_name=script_name,
            type_check=type_check,
        )

        # Execute with inputs and external functions
        result = m.run(inputs=inputs, external_functions=func_dict)

        # Convert Monty output to JSON-serializable format
        return {"status": "success", "output": str(result)}

    except pydantic_monty.MontyRuntimeError as e:
        return {"status": "error", "error": "Runtime error", "details": str(e)}
    except pydantic_monty.MontySyntaxError as e:
        return {"status": "error", "error": "Syntax error", "details": str(e)}
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {type(e).__name__}",
            "details": str(e),
        }


def execute_from_file(file_path, inputs=None, external_functions=None):
    """
    Execute Python code from a file using Monty

    Args:
        file_path: Path to Python file
        inputs: Dict of input variables
        external_functions: Dict of external functions

    Returns:
        Execution result dict
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        script_name = os.path.basename(file_path)
        return execute_code(
            code,
            inputs=inputs,
            external_functions=external_functions,
            script_name=script_name,
        )

    except FileNotFoundError:
        return {"status": "error", "error": "File not found", "details": file_path}
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to read file: {type(e).__name__}",
            "details": str(e),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Monty Executor - Secure Python code sandbox with external functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple execution
  %(prog)s --code 'result = sum(range(10)); print(result)'

  # With inputs
  %(prog)s --code 'x + y' --inputs '{"x": 10, "y": 20}'

  # With external functions
  %(prog)s --code 'news = fetch_news("hackernews", 5); print(len(news))' --use-external-funcs

  # From file
  %(prog)s --file script.py --inputs '{"data": [1,2,3]}'

  # List available external functions
  %(prog)s --list-external-funcs
        """,
    )

    # Execution source
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--code", help="Python code to execute")
    group.add_argument("--file", help="Python file to execute")

    # Options
    parser.add_argument("--inputs", help="Inputs as JSON string")
    parser.add_argument(
        "--use-external-funcs",
        action="store_true",
        help="Load and use external functions from external_functions.py",
    )
    parser.add_argument(
        "--list-external-funcs",
        action="store_true",
        help="List available external functions and exit",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Execution timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--memory", type=int, default=128, help="Memory limit in MB (informational)"
    )
    parser.add_argument(
        "--script-name", default="script.py", help="Script name for error messages"
    )

    args = parser.parse_args()

    # Load external functions if requested
    external_functions = None
    if args.use_external_funcs or args.list_external_funcs:
        try:
            from external_functions import (
                get_external_functions,
                list_external_functions,
            )

            if args.list_external_funcs:
                print("Available External Functions:")
                print("=" * 60)
                funcs = list_external_functions()
                for name, desc in sorted(funcs.items()):
                    print(f"\n{name}:")
                    print(f"  {desc}")
                sys.exit(0)

            external_functions = get_external_functions()
        except ImportError as e:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "error": "Failed to load external_functions.py",
                        "details": str(e),
                    }
                ),
                file=sys.stderr,
            )
            sys.exit(1)

    # Parse inputs
    inputs = None
    if args.inputs:
        try:
            inputs = json.loads(args.inputs)
        except json.JSONDecodeError as e:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "error": "Invalid JSON in --inputs",
                        "details": str(e),
                    }
                ),
                file=sys.stderr,
            )
            sys.exit(1)

    # Execute
    if args.file:
        result = execute_from_file(
            args.file, inputs=inputs, external_functions=external_functions
        )
    else:
        result = execute_code(
            args.code,
            inputs=inputs,
            external_functions=external_functions,
            script_name=args.script_name,
            type_check=False,
        )

    # Output result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
