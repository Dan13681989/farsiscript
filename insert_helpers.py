import sys

with open('gen_compiler.py', 'rb') as f:
    data = f.read()

# Helper functions block (as it must appear inside the generator's string tuple)
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

# Locate the end of the current_time function
pos = data.find(b"'current_time() {\\n'")
if pos == -1:
    print("ERROR: current_time marker not found")
    sys.exit(1)

end_pos = data.find(b"'}\\n\\n'", pos + 1)
if end_pos == -1:
    print("ERROR: end of current_time not found")
    sys.exit(1)

# Move past the newline after the closing quote
end_line_pos = data.find(b'\n', end_pos)
if end_line_pos == -1:
    end_line_pos = end_pos + len(b"'}\\n\\n'")
else:
    end_line_pos += 1

# Insert helpers
data = data[:end_line_pos] + helpers + data[end_line_pos:]

# Fix system() semicolon
old_sys = b"return f'system({cmd})'"
new_sys = b"return f'system({cmd});'"
if old_sys in data:
    data = data.replace(old_sys, new_sys, 1)
    print("Semicolon fixed")
else:
    print("Semicolon line not found – checking for already fixed version")
    if b"return f'system({cmd});'" not in data:
        print("WARNING: semicolon may still be missing")

with open('gen_compiler.py', 'wb') as f:
    f.write(data)
print("Helpers inserted and semicolon fixed")
