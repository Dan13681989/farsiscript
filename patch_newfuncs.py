# patch_newfuncs.py - safely add تاریخ_امروز, خروجی, etc.
with open('compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ---- A) Add type info in infer_type ----
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647': return 'void'" in line:
        new_types = [
            "            if node.name == '\\u062e\\u0631\\u0648\\u062c\\u06cc': return 'string'\n",
            "            if node.name == '\\u062a\\u0627\\u0631\\u06cc\\u062e_\\u0627\\u0645\\u0631\\u0648\\u0632': return 'string'\n",
            "            if node.name == '\\u0648\\u0631\\u0648\\u062f\\u06cc_\\u067e\\u0646\\u0647\\u0627\\u0646': return 'string'\n",
        ]
        for j, nt in enumerate(new_types):
            lines.insert(i + 1 + j, nt)
        break

# ---- B) Add helper C functions (current_date, read_pipe) after current_time ----
for i, line in enumerate(lines):
    if 'char* current_time()' in line:
        # find the end of the function: the line that contains '}\n' after current_time
        # we'll insert after the '}\n\n' that ends current_time
        # the function ends around 6 lines later
        end_func = None
        for k in range(i, len(lines)):
            if lines[k] == '}\n' and k > i + 4:
                end_func = k + 1  # after the newline following }
                break
        if end_func:
            helpers = [
                "char* current_date() {\n",
                "    time_t now = time(NULL);\n",
                "    struct tm* t = localtime(&now);\n",
                "    static char buf[11];\n",
                "    strftime(buf, sizeof(buf), \"%Y-%m-%d\", t);\n",
                "    return buf;\n",
                "}\n\n",
                "char* read_pipe(const char* cmd) {\n",
                "    FILE* fp = popen(cmd, \"r\");\n",
                "    if (!fp) return \"\";\n",
                "    static char buf[4096];\n",
                "    size_t n = fread(buf, 1, sizeof(buf)-1, fp);\n",
                "    buf[n] = '\\0';\n",
                "    pclose(fp);\n",
                "    return buf;\n",
                "}\n\n"
            ]
            for j, h in enumerate(helpers):
                lines.insert(end_func + j, h)
            print("Helpers inserted")
        break

# ---- C) Insert functions in gen_expr after خطا_بده ----
target = None
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647':" in line and 'gen_expr' in lines[i-3]:
        target = i + 2  # after the return arg line
        break
if target:
    lib_expr = [
        "            if node.name == '\\u062e\\u0631\\u0648\\u062c\\u06cc':\n",
        "                cmd = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        "                return f'read_pipe({cmd})'\n",
        "            if node.name == '\\u062a\\u0627\\u0631\\u06cc\\u062e_\\u0627\\u0645\\u0631\\u0648\\u0632':\n",
        "                return 'current_date()'\n",
    ]
    for j, l in enumerate(lib_expr):
        lines.insert(target + j, l)
    print("gen_expr updated")

# ---- D) Insert functions in gen_stmt after خطا_بده ----
target_stmt = None
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647':" in line and 'gen_stmt' in lines[i-3]:
        target_stmt = i + 2
        break
if target_stmt:
    lib_stmt = [
        "            if node.name == '\\u062e\\u0631\\u0648\\u062c\\u06cc':\n",
        "                cmd = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        "                return f'printf(\"%s\", read_pipe({cmd}))'\n",
        "            if node.name == '\\u062a\\u0627\\u0631\\u06cc\\u062e_\\u0627\\u0645\\u0631\\u0648\\u0632':\n",
        "                return 'printf(\"%s\", current_date());'\n",
    ]
    for j, l in enumerate(lib_stmt):
        lines.insert(target_stmt + j, l)
    print("gen_stmt updated")

# ---- E) Fix اجرا to not print exit code ----
for i, line in enumerate(lines):
    if "return f'system({cmd})'" in line and 'gen_stmt' in lines[i-3]:
        lines[i] = "                return f'system({cmd});'\n"
        print("Fixed اجرا")
        break

with open('compiler.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("compiler.py successfully patched")