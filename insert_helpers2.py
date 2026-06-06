import sys

with open('gen_compiler.py', 'rb') as f:
    data = f.read()

# In gen_compiler.py, the current_time function starts with:
#             'char* current_time() {\n'
# which in raw bytes is: b"            'char* current_time() {\\n'"
# (there's a double backslash before the n)
marker = b"            'char* current_time() {\\n'"
pos = data.find(marker)
if pos == -1:
    # Maybe the indentation is different – let's search a simpler substring
    # Look for the unique part: "char* current_time()"
    pos = data.find(b"char* current_time()")
    if pos == -1:
        print("ERROR: current_time definition not found")
        sys.exit(1)
    else:
        print("Found marker at", pos)

# The function ends with the line:             '}\\n\\n'
# which is bytes: b"            '}\\n\\n'"
end_marker = b"            '}\\n\\n'"
end_pos = data.find(end_marker, pos + 1)
if end_pos == -1:
    print("ERROR: end of current_time not found")
    sys.exit(1)

# Move past the ending newline after that line
end_line_pos = data.find(b'\n', end_pos)
if end_line_pos == -1:
    end_line_pos = end_pos + len(end_marker)
else:
    end_line_pos += 1

# Insert the helper functions
helpers = b"""            'char* current_date() {\\n'
            '    time_t now = time(NULL);\\n'
            '    struct tm* t = localtime(&now);\\n'
            '    static char buf[11];\\n'
            '    strftime(buf, sizeof(buf), "%Y-%m-%d", t);\\n'
            '    return buf;\\n'
            '}\\n\\n'
            'char* read_pipe(const char* cmd) {\\n'
            '    FILE* fp = popen(cmd, "r");\\n'
            '    if (!fp) return "";\\n'
            '    static char buf[4096];\\n'
            '    size_t n = fread(buf, 1, sizeof(buf)-1, fp);\\n'
            '    buf[n] = \\'\\\\0\\';\\n'
            '    pclose(fp);\\n'
            '    return buf;\\n'
            '}\\n\\n'
"""

data = data[:end_line_pos] + helpers + data[end_line_pos:]

# Fix semicolon for system() in gen_stmt
old_sys = b"return f'system({cmd})'"
new_sys = b"return f'system({cmd});'"
if old_sys in data:
    data = data.replace(old_sys, new_sys, 1)
    print("Semicolon fixed")
else:
    # maybe already fixed
    if b"return f'system({cmd});'" in data:
        print("Semicolon already fixed")
    else:
        print("WARNING: semicolon line not found")

with open('gen_compiler.py', 'wb') as f:
    f.write(data)
print("Helpers inserted and semicolon fixed")
