#!/usr/bin/env python3
"""Simple step-through debugger for FarsiScript."""
import sys
from .tokenizer import Lexer
from .parser import Parser
from .evaluator import Environment, evaluate

def debug_code(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code.split('\n'))
    ast = parser.parse()
    env = Environment()
    functions = {}
    for i, stmt in enumerate(ast):
        print(f"[Step {i+1}] Executing: {stmt}")
        input("Press Enter to continue...")
        try:
            result = evaluate(stmt, env, functions)
            if result is not None:
                print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    if len(sys.argv) < 2:
        print("Usage: fs debug <file.fs>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()
    debug_code(code)

if __name__ == '__main__':
    main()
