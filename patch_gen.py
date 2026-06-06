# patch_gen.py - inserts new builtins into gen_compiler.py

with open('gen_compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# --- A) Add return types in infer_type ---
for i, line in enumerate(lines):
    if "if node.name == '\\u062e\\u0637\\u0627_\\u0628\\u062f\\u0647': return 'void'" in line:
        new_types = [
            "            if node.name == '\\u062e\\u0631\\u0648\\u062c\\u06cc': return 'string'\n",
            "            if node.name == '\\u062a\\u0627\\u0631\\u06cc\\u062e_\\u0627\\u0645\\u0631\\u0648\\u0632': return 'string'\n",
            "            if node.name == '\\u0648\\u0631\\u0648\\u062f\\u06cc_\\u067e\\u0646\\u0647\\u0627\\u0646': return 'string'\n",
        ]
        for j, nt in enumerate(new_types):
            lines.insert(i + 1 + j, nt)
        print("Types added")
        break

# --- B) Add C helper functions after current_time ---
for i, line in enumerate(lines):
    if "'char* current_time() {\n'" in line:
        # find the closing "}\n\n'" of current_time (it's part of a tuple of strings)
        end_idx = None
        for k in range(i, min(i+20, len(lines))):
            if lines[k].strip() == "'}\\n\\n'":
                end_idx = k
                break
        if end_idx:
            helpers = [
                "            'char* current_date() {\\n'\n",
                "            '    time_t now = time(NULL);\\n'\n",
                "            '    struct tm* t = localtime(&now);\\n'\n",
                "            '    static char buf[11];\\n'\n",
                "            '    strftime(buf, sizeof(buf), \"%Y-%m-%d\", t);\\n'\n",
                "            '    return buf;\\n'\n",
                "            '}\\n\\n'\n",
                "            'char* read_pipe(const char* cmd) {\\n'\n",
                "            '    FILE* fp = popen(cmd, \"r\");\\n'\n",
                "            '    if (!fp) return \"\";\\n'\n",
                "            '    static char buf[4096];\\n'\n",
                "            '    size_t n = fread(buf, 1, sizeof(buf)-1, fp);\\n'\n",
                "            '    buf[n] = \\'\\\\0\\';\\n'\n",
                "            '    pclose(fp);\\n'\n",
                "            '    return buf;\\n'\n",
                "            '}\\n\\n'\n",
            ]
            for j, h in enumerate(helpers):
                lines.insert(end_idx + 1 + j, h)
            print("Helpers added")
        break

# --- C) Insert builtin handlers in gen_expr (after اجرا block) ---
target = None
for i, line in enumerate(lines):
    if "if node.name == '\\u0627\\u062c\\u0631\\u0627':" in line and 'gen_expr' in lines[i-3]:
        target = i + 2  # after the return line
        break
if target:
    new_expr = [
        "            if node.name == '\\u062e\\u0631\\u0648\\u062c\\u06cc':\n",
        "                cmd = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        "                return f'read_pipe({cmd})'\n",
        "            if node.name == '\\u062a\\u0627\\u0631\\u06cc\\u062e_\\u0627\\u0645\\u0631\\u0648\\u0632':\n",
        "                return 'current_date()'\n",
        "            if node.name == '\\u0648\\u0631\\u0648\\u062f\\u06cc_\\u067e\\u0646\\u0647\\u0627\\u0646':\n",
        "                return '\"<hidden>\"'\n",
    ]
    for j, l in enumerate(new_expr):
        lines.insert(target + j, l)
    print("gen_expr updated")

# --- D) Insert builtin handlers in gen_stmt (after اجرا block) ---
target_stmt = None
for i, line in enumerate(lines):
    if "if node.name == '\\u0627\\u062c\\u0631\\u0627':" in line and 'gen_stmt' in lines[i-3]:
        target_stmt = i + 2  # after the return line
        break
if target_stmt:
    new_stmt = [
        "            if node.name == '\\u062e\\u0631\\u0648\\u062c\\u06cc':\n",
        "                cmd = gen_expr(node.args[0], func_name, local_vars, decls)\n",
        "                return f'printf(\"%s\", read_pipe({cmd}))'\n",
        "            if node.name == '\\u062a\\u0627\\u0631\\u06cc\\u062e_\\u0627\\u0645\\u0631\\u0648\\u0632':\n",
        "                return 'printf(\"%s\", current_date());'\n",
        "            if node.name == '\\u0648\\u0631\\u0648\\u062f\\u06cc_\\u067e\\u0646\\u0647\\u0627\\u0646':\n",
        "                return 'printf(\"<hidden>\\\\n\");'\n",
    ]
    for j, l in enumerate(new_stmt):
        lines.insert(target_stmt + j, l)
    print("gen_stmt updated")

# --- E) Fix اجرا to add semicolon in gen_stmt ---
for i, line in enumerate(lines):
    if "return f'system({cmd})'" in line and 'gen_stmt' in lines[i-3]:
        lines[i] = "                return f'system({cmd});'\n"
        print("Fixed اجرا semicolon")
        break

with open('gen_compiler.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("gen_compiler.py patched successfully")