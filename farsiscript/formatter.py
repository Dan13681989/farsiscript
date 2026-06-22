#!/usr/bin/env python3
"""FarsiScript code formatter."""
import sys
import re

def format_code(code):
    lines = code.split('\n')
    result = []
    indent_level = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            result.append(stripped)
            continue
        # Add missing semicolons to statements
        if (re.match(r'(چاپ|خواندن|برگردان|خطا_بده|نوشتن_فایل|خواندن_فایل|حذف_فایل|دریافت_از_وب)\s', stripped) and not stripped.endswith(';')):
            stripped += ';'
        # Adjust indentation based on braces
        if stripped.endswith('{'):
            result.append('    ' * indent_level + stripped)
            indent_level += 1
        elif stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)
            result.append('    ' * indent_level + stripped)
        else:
            result.append('    ' * indent_level + stripped)
    return '\n'.join(result) + '\n'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fs fmt <file.fs>")
        sys.exit(1)
    for filepath in sys.argv[1:]:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        formatted = format_code(original)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)
        print(f"Formatted {filepath}")
