import sys
from .tokenizer import Lexer
from .parser import PrintNode, Parser
from .evaluator import Environment, evaluate

def run_farsi_script(code):
    """Interpret FarsiScript code string and print output."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    source_lines = code.split('\n')
    source_lines = code.split('\n')
    parser = Parser(tokens, source_lines)
    ast = parser.parse()
    env = Environment()
    functions = {}
    for stmt in ast:
        try:
            evaluate(stmt, env, functions)
        except Exception as e:
            print(f"خطا: {e}")


def repl():
    print("FarsiScript REPL (type .exit to quit)")
    env = Environment()
    functions = {}
    while True:
        try:
            code = input(">>> ")
            if code.strip() == ".exit":
                break
            if not code.strip():
                continue
            from .tokenizer import Lexer
            from .parser import Parser
            tokens = Lexer(code).tokenize()
            ast = Parser(tokens, code.split('\n')).parse()
            for stmt in ast:
                result = evaluate(stmt, env, functions)
                if not isinstance(stmt, PrintNode) and result is not None:
                    print(result)
        except Exception as e:
            print(f"خطا: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: fs <command> [file]")
        print("Commands: compile, run, repl, fmt, debug, install")
        sys.exit(1)
    command = sys.argv[1]
    if command == 'check':
        from .type_checker import check_file
        for filepath in sys.argv[2:]:
            check_file(filepath)
        return
    if command == 'repl':
        repl()
        return
    elif command == 'fmt':
        from .formatter import format_code
        for filepath in sys.argv[2:]:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            formatted = format_code(original)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted)
            print(f"Formatted {filepath}")
        return
    elif command == 'debug':
        from .debugger import debug_code
        for filepath in sys.argv[2:]:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            debug_code(code)
        return
    elif command == 'install':
        from .pkg_manager import main as pkg_main
        import sys as _sys
        _sys.argv = [_sys.argv[0]] + _sys.argv[2:]
        pkg_main()
        return
    # Original compile/run commands
    if command == 'compile':
        if len(sys.argv) < 3:
            print("Usage: fs compile <file.fs>")
            sys.exit(1)
        input_file = sys.argv[2]
        output_exe = input_file.rsplit('.', 1)[0]
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
        from .compiler import compile_to_c
        compile_to_c(code, output_exe)
    elif command == 'run':
        if len(sys.argv) < 3:
            print("Usage: fs run <file.fs>")
            sys.exit(1)
        input_file = sys.argv[2]
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
        run_farsi_script(code)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()

