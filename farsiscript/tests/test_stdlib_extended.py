import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from farsiscript.main import run_farsi_script

class TestExtendedStdlib(unittest.TestCase):
    def run_code(self, code):
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            run_farsi_script(code)
        finally:
            sys.stdout = old_stdout

    def test_sqrt(self):
        self.run_code('چاپ ریشه_دوم(9);')

    def test_abs(self):
        self.run_code('چاپ قدر_مطلق(5);')

    def test_ceil(self):
        self.run_code('چاپ سقف(3.14);')

    def test_floor(self):
        self.run_code('چاپ کف(3.14);')

    def test_strlen(self):
        self.run_code('چاپ طول_رشته("سلام");')

    def test_upper(self):
        self.run_code('چاپ بزرگکن("hello");')

    def test_lower(self):
        self.run_code('چاپ کوچککن("HELLO");')

    def test_format_date(self):
        self.run_code('چاپ فرمت_تاریخ("امروز %Y/%m/%d");')

    def test_str_repeat(self):
        self.run_code('چاپ تکرار_رشته("ها", 3);')

    def test_typeof(self):
        self.run_code('x = 10; چاپ نوع(x);')

    def test_array_len(self):
        self.run_code('چاپ طول_آرایه([1,2,3]);')

    def test_read_file(self):
        self.run_code('نوشتن_فایل("test_fs_temp.txt", "محتوای تست");')
        self.run_code('چاپ خواندن_فایل("test_fs_temp.txt");')

    def test_write_file(self):
        self.run_code('چاپ نوشتن_فایل("test_fs_write.txt", "سلام");')

    def test_shamsi_date(self):
        self.run_code('چاپ تاریخ_شمسی();')

    def test_pow(self):
        self.run_code('چاپ توان(2, 3);')
    def test_sin(self):
        self.run_code('چاپ سینوس(0);')
    def test_cos(self):
        self.run_code('چاپ کسینوس(0);')
    def test_log(self):
        self.run_code('چاپ لگاریتم(1);')
    def test_sort(self):
        self.run_code('چاپ مرتب_سازی([3,1,2]);')
    def test_list_files(self):
        self.run_code('چاپ لیست_فایل_ها(".");')
    def test_delete_file(self):
        self.run_code('چاپ حذف_فایل("__temp_test_delete__.txt");')

    def test_fetch_url(self):
        self.run_code('چاپ دریافت_از_وب("https://httpbin.org/get");')

    def test_json_read(self):
        self.run_code('چاپ خواندن_جیسون("[1,2,3]");')

    def test_json_write(self):
        self.run_code('چاپ نوشتن_جیسون({"a":1});')


if __name__ == '__main__':
    unittest.main()

    def test_read_file(self):
        self.run_code('نوشتن_فایل("test_fs_temp.txt", "محتوای تست");')
        self.run_code('چاپ خواندن_فایل("test_fs_temp.txt");')

    def test_write_file(self):
        self.run_code('چاپ نوشتن_فایل("test_fs_write.txt", "سلام");')

    def test_str_reverse(self):
        self.run_code('چاپ برعکس_رشته("سلام");')

    def test_today_date(self):
        self.run_code('چاپ تاریخ_امروز();')

    def test_str_strip(self):
        self.run_code('چاپ حذف_فاصله("   سلام   ");')

    def test_json_read(self):
        self.run_code('چاپ خواندن_جیسون(' + "'" + '{"a":1}' + "'" + ');')
