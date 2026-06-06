import sys
from tokenizer import Lexer
from parser import Parser
from evaluator import evaluate, Environment


def run_farsi_script(code):
    lexer = Lexer(code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parse()
    env = Environment()
    functions = {}
    try:
        for stmt in ast:
            evaluate(stmt, env, functions)
    except Exception as e:
        print(f"\u062e\u0637\u0627: {e}")
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            print(f"{i:4}: {line}")
        raise

def main():
    if len(sys.argv) < 3:
        print("استفاده: farsiscript run|compile <file.fs>")
        sys.exit(1)
    mode = sys.argv[1]
    file = sys.argv[2]
    with open(file, 'r', encoding='utf-8') as f:
        code = f.read()
    if mode == 'run':
        run_farsi_script(code)
    elif mode == 'compile':
        from compiler import compile_to_c
        out = file.replace('.fs', '.c')
        compile_to_c(code, out)
    else:
        print("حالت نامعتبر")

if __name__ == '__main__':
    main()

import traceback

def run_farsi_script(code):
    lexer = Lexer(code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parse()
    env = Environment()
    functions = {}
    try:
        for stmt in ast:
            evaluate(stmt, env, functions)
    except Exception as e:
        print(f"خطا: {e}")
        # Print source with line numbers
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            print(f"{i:4}: {line}")
        raise
