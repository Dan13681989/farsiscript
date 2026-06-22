c_code = '''#include <stdio.h>
int main() {
    printf("Hello from selfhost!\\n");
    return 0;
}
'''
with open("test_self.fs.c", "w") as f:
    f.write(c_code)
print("C code written to test_self.fs.c")
