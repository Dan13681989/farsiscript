#!/usr/bin/env python3
"""Linter ساده برای فارسی‌اسکریپت"""
import sys
import re

def lint_code(code):
    lines = code.split('\n')
    issues = []
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            continue
        # نقطه‌ویرگول فراموش شده
        if re.match(r'(چاپ|خواندن|برگردان|خطا_بده|استفاده از|نوشتن_فایل|خواندن_فایل)\s', stripped) and not stripped.endswith(';'):
            issues.append((i, "گفتهٔ دستوری بدون نقطه‌ویرگول (;)"))

        # فاصله‌های اضافی
        if '  ' in line and not line.lstrip().startswith('//'):
            issues.append((i, "فاصله‌های اضافی"))

        # فاصلهٔ انتهای خط
        if line != line.rstrip():
            issues.append((i, "فاصلهٔ خالی در انتهای خط"))

        # تورفتگی نامنظم
        indent = len(line) - len(line.lstrip())
        if indent % 4 != 0:
            issues.append((i, "تورفتگی باید مضربی از ۴ فاصله باشد"))

    return issues

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: linter.py <file.fs>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    for line_num, msg in lint_code(code):
        print(f"خط {line_num}: {msg}")
