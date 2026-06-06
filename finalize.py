#!/usr/bin/env python3
import os

# --- README.md ---
readme = r"""# زبان برنامه‌نویسی فارسی – FarsiScript

یک زبان برنامه‌نویسی کاملاً فارسی با مفسر (interpreter) و کامپایلر به زبان C.

## 🚀 شروع سریع

```bash
# اجرای یک فایل
./fs run برنامه.fs

# کامپایل به C و اجرا
./fs compile برنامه.fs
📚 قابلیت‌ها

قابلیت	مثال
متغیرها و عملگرها	x = 5 + 2 * 3
رشته‌ها و الحاق	"سلام " + "حسام"
شرط چندگانه	اگر (نمره > 90) { ... } درغیراینصورت اگر ...
حلقه‌ها	تاوقتی, برای عددی, برای روی آرایه/رشته/فرهنگ
توابع	تابع جمع(a, b) { برگردان a + b; }
آرایه‌ها	[1, 2, 3] و arr[0] = 10
فرهنگ‌ها (دیکشنری)	{"اسم": "حسام", "سن": 30}
ورودی/خروجی	خواندن, چاپ
کار با فایل	خواندن_فایل, نوشتن_فایل
مدیریت خطا	سعی کن { ... } بگیر (خطا) { ... }
کلاس‌ها و اشیاء	کلاس شخص { ... }
اعداد فارسی	۳.۱۴ و ورودی فارسی
نظرات	// توضیح
کامپایل به C	./fs compile file.fs
🛠 نصب

bash
pip install -e .
# یا
python setup.py install
پس از نصب، دستور farsiscript در دسترس خواهد بود.

📖 مثال‌های بیشتر

کلاس‌ها و اشیاء

farsi
کلاس شخص {
    تابع جدید(نام, سن) {
        این.نام = نام;
        این.سن = سن;
    }
    تابع معرفی() {
        چاپ "اسم: " + این.نام + " سن: " + این.سن;
    }
}
حسام = شخص("حسام", 30);
حسام.معرفی();
مدیریت خطا

farsi
سعی کن {
    خطا_بده("مشکل در برنامه");
} بگیر (خطا) {
    چاپ "خطا رخ داد: " + خطا;
}
وارد کردن ماژول

farsi
استفاده از "کتابخانه.fs";
سلام("حسام");
📁 ساختار پروژه

tokenizer.py – تحلیل واژگان
parser.py – تحلیل نحوی
evaluator.py – اجرا (مفسر)
compiler.py – تولید کد C و کامپایل
main.py – نقطهٔ شروع مفسر
fs – ابزار خط فرمان یکپارچه
🤝 مشارکت

ایده‌ها و پیشنهادها خوش‌آمدند!
برای توسعه، فایل‌های .py را ویرایش کنید و با ./fs run تست بگیرید.

📝 مجوز

پروژه به صورت آزاد و رایگان ارائه می‌شود.
هرگونه استفاده، تغییر و انتشار با ذکر منبع مجاز است.

ساخته‌شده با عشق به فارسی 💚
"""

with open('README.md', 'w', encoding='utf-8') as f:
f.write(readme)
print('✅ README.md created')

--- setup.py ---

setup_code = r'''from setuptools import setup

setup(
name='farsiscript',
version='1.0.0',
description='یک زبان برنامه\u200cنویسی فارسی با مفسر و کامپایلر',
author='شما',
py_modules=['tokenizer', 'parser', 'evaluator', 'compiler', 'main'],
entry_points={
'console_scripts': [
'farsiscript=main:main',
],
},
install_requires=[],
)
'''
with open('setup.py', 'w', encoding='utf-8') as f:
f.write(setup_code)
print('✅ setup.py created')

--- add main() to main.py if needed ---

with open('main.py', 'r') as f:
main_content = f.read()

if 'def main():' not in main_content:
main_extra = r'''

def main():
import sys
if len(sys.argv) < 3:
print("استفاده: farsiscript run|compile <file.fs>")
sys.exit(1)
mode = sys.argv[1]
file = sys.argv[2]
with open(file, 'r', encoding='utf-8') as f:
code = f.read()
if mode == 'run':
run_farsi_script(code)
elif mode == 'compile':
from compiler import compile_to_c
out = file.replace('.fs', '.c')
compile_to_c(code, out)
else:
print("حالت نامعتبر")
'''
with open('main.py', 'a') as f:
f.write(main_extra)
print('✅ main() added to main.py')
else:
print('ℹ️ main() already exists')
