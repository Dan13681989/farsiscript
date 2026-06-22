// کتابخانهٔ الگویابی (regex)

تابع تطبیق_الگو(الگو, متن) {
    چاپ اجرا("python3 lib/regex_helper.py match " + الگو + " " + متن);
}

تابع همه_تطبیق_ها(الگو, متن) {
    چاپ اجرا("python3 lib/regex_helper.py findall " + الگو + " " + متن);
}

تابع جایگزینی_الگو(الگو, جایگزین, متن) {
    چاپ اجرا("python3 lib/regex_helper.py replace " + الگو + " " + جایگزین + " " + متن);
}

تابع تقسیم_با_الگو(الگو, متن) {
    چاپ اجرا("python3 lib/regex_helper.py split " + الگو + " " + متن);
}
