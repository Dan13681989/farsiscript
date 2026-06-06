#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 2:
    print("استفاده: fs run|compile <file.fs>")
    sys.exit(1)

mode = sys.argv[1]
if mode == "run":
    from main import run_farsi_script
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        code = f.read()
    run_farsi_script(code)
elif mode == "compile":
    from compiler import compile_to_c
    inp = sys.argv[2]
    outc = inp.replace('.fs', '.c') if len(sys.argv) < 4 else sys.argv[3]
    with open(inp, 'r', encoding='utf-8') as f:
        code = f.read()
    compile_to_c(code, outc)
else:
    print("حالت نامعتبر. از run یا compile استفاده کنید.")
