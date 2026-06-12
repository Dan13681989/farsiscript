import sys
from .tokenizer import Lexer
from .parser import Parser
from .evaluator import Environment, evaluate

def run_farsi_script(code):
    """Interpret FarsiScript code string and print output."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    env = Environment()
    functions = {}
    for stmt in ast:
        try:
            evaluate(stmt, env, functions)
        except Exception as e:
            print(f"خطا: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: fs <input.fs>")
        sys.exit(1)
    input_file = sys.argv[1]
    with open(input_file, 'r', encoding='utf-8') as f:
        code = f.read()
    run_farsi_script(code)

if __name__ == '__main__':
    main()
