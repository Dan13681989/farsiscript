// کتابخانهٔ لاک‌پشت فارسی

تابع حرکت_جلو(فاصله) {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.forward(" + فاصله + ")");
    اجرا("python3 __turtle__.py");
}

تابع چرخش_راست(زاویه) {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.right(" + زاویه + ")");
    اجرا("python3 __turtle__.py");
}

تابع چرخش_چپ(زاویه) {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.left(" + زاویه + ")");
    اجرا("python3 __turtle__.py");
}

تابع قلم_بالا() {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.penup()");
    اجرا("python3 __turtle__.py");
}

تابع قلم_پایین() {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.pendown()");
    اجرا("python3 __turtle__.py");
}

تابع رنگ_قلم(رنگ) {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.pencolor('" + رنگ + "')");
    اجرا("python3 __turtle__.py");
}

تابع پایان() {
    نوشتن_فایل("__turtle__.py", "import turtle\nturtle.done()");
    اجرا("python3 __turtle__.py");
}
