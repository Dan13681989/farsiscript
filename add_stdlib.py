import os

with open('compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Add #include <time.h>
for i, line in enumerate(lines):
    if line.startswith("c_code = '#include <stdio.h>"):
        lines[i] = "c_code = '#include <stdio.h>\\n#include <string.h>\\n#include <stdlib.h>\\n#include <stdint.h>\\n#include <setjmp.h>\\n#include <signal.h>\\n#include <time.h>\\n\\n'\n"
        break

# 2. Add current_time helper after the __try_signal_handler function
for i, line in enumerate(lines):
    if 'longjmp(__try_buf, 1);' in line and '__try_signal_handler' in lines[i-2]:
        insert_pos = i + 2  # after the closing '}' line
        helper = [
            "char* current_time() {\n",
            "    time_t now = time(NULL);\n",
            "    char* s = asctime(localtime(&now));\n",
            "    s[strlen(s)-1] = '\\0';\n",
            "    return s;\n",
            "}\n\n"
        ]
        for j, h in enumerate(helper):
            lines.insert(insert_pos + j, h)
        break

# 3. Add library functions in gen_expr (after the خطا_بده block)
target = None
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647':" in line and 'gen_expr' in lines[i-3]:
        target = i + 2  # after "return arg"
        break
if target:
    lib_expr = [
        "            if node.name == '\\u0632\\u0645\\u0627\\u0646_\\u0627\\u06a9\\u0646\\u0648\\u0646':\n",
        "                return 'current_time()'\n",
        "            if node.name == '\\u0639\\u062f\\u062f_\\u062a\\u0635\\u0627\\u062f\\u0641\\u06cc':\n",
        "                low = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        "                high = gen_expr(node.args[1], func_name, local_vars, decls)\n",
        r"                return f'((rand() % (int)({high} - {low} + 1)) + (int){low})'" + "\n",
        "            if node.name == '\\u0627\\u062c\\u0631\\u0627':\n",
        "                cmd = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        r"                return f'system({cmd})'" + "\n",
    ]
    for j, l in enumerate(lib_expr):
        lines.insert(target + j, l)

# 4. Add library functions in gen_stmt (after the خطا_بده block)
target_stmt = None
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647':" in line and 'gen_stmt' in lines[i-3]:
        target_stmt = i + 2
        break
if target_stmt:
    lib_stmt = [
        "            if node.name == '\\u0632\\u0645\\u0627\\u0646_\\u0627\\u06a9\\u0646\\u0648\\u0646':\n",
        r"                return 'printf(\"%s\", current_time());'" + "\n",
        "            if node.name == '\\u0639\\u062f\\u062f_\\u062a\\u0635\\u0627\\u062f\\u0641\\u06cc':\n",
        "                low = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        "                high = gen_expr(node.args[1], func_name, local_vars, decls)\n",
        r"                return f'printf(\"%d\\n\", ((rand() % (int)({high} - {low} + 1)) + (int){low}))'" + "\n",
        "            if node.name == '\\u0627\\u062c\\u0631\\u0627':\n",
        "                cmd = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        r"                return f'system({cmd})'" + "\n",
    ]
    for j, l in enumerate(lib_stmt):
        lines.insert(target_stmt + j, l)

# 5. Add type information in infer_type for the new functions
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647': return 'void'" in line:
        new_types = [
            "            if node.name == '\\u0632\\u0645\\u0627\\u0646_\\u0627\\u06a9\\u0646\\u0648\\u0646': return 'string'\n",
            "            if node.name == '\\u0639\\u062f\\u062f_\\u062a\\u0635\\u0627\\u062f\\u0641\\u06cc': return 'int'\n",
            "            if node.name == '\\u0627\\u062c\\u0631\\u0627': return 'int'\n",
        ]
        for j, nt in enumerate(new_types):
            lines.insert(i + 1 + j, nt)
        break

# 6. Add srand(time(NULL)); at the start of main()
for i, line in enumerate(lines):
    if line == "    c_code += 'int main() {\\n'\n":
        lines.insert(i+1, "    c_code += '    srand(time(NULL));\\n'\n")
        break

# 7. Handle 'int' type in PrintNode (gen_stmt)
for i, line in enumerate(lines):
    if "elif typ == 'double':" in line and "printf" in lines[i+1]:
        lines.insert(i, "            elif typ == 'int':\n                return f'printf(\"%d\\n\", {e});'\n")
        break

with open('compiler.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Standard library added successfully")
