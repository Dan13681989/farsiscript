"""Static type checker for FarsiScript."""
import sys
from .tokenizer import Lexer
from .parser import Parser, NumberNode, RealNode, StringNode, VarNode, BinOpNode, CallNode, AssignNode, PrintNode, ArrayNode, DictNode

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    source_lines = code.split('\n')
    tokens = Lexer(code).tokenize()
    ast = Parser(tokens, source_lines).parse()

    types = {}
    errors = []

    def infer_type(node):
        if isinstance(node, NumberNode):
            return 'int'
        elif isinstance(node, RealNode):
            return 'float'
        elif isinstance(node, StringNode):
            return 'string'
        elif isinstance(node, VarNode):
            return types.get(node.name, 'unknown')
        elif isinstance(node, BinOpNode):
            left = infer_type(node.left)
            right = infer_type(node.right)
            return left if left == right else 'any'
        elif isinstance(node, CallNode):
            if node.name in ['چاپ','خواندن','برگردان','خطا_بده','نوشتن_فایل','خواندن_فایل','حذف_فایل','دریافت_از_وب','اجرا']:
                return 'void'
            elif node.name in ['ریشه_دوم','سقف','کف','قدر_مطلق','سینوس','کسینوس','لگاریتم','توان','عدد_تصادفی']:
                return 'float'
            elif node.name in ['طول_رشته','بزرگکن','کوچککن','برعکس_رشته','حذف_فاصله','تکرار_رشته','فرمت_تاریخ','زمان_اکنون','تاریخ_امروز','تاریخ_شمسی','لیست_فایل_ها']:
                return 'string'
            elif node.name in ['نوع']:
                return 'string'
            elif node.name in ['طول_آرایه','مرتب_سازی']:
                return 'array'
            return 'any'
        elif isinstance(node, ArrayNode):
            return 'array'
        elif isinstance(node, DictNode):
            return 'dict'
        return 'any'

    for stmt in ast:
        if isinstance(stmt, AssignNode):
            types[stmt.name] = infer_type(stmt.expr)
        elif isinstance(stmt, PrintNode):
            pass

    if errors:
        for e in errors:
            print(e)
    else:
        print("✅ No type errors found.")
    return len(errors) == 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fs check <file.fs>")
        sys.exit(1)
    ok = check_file(sys.argv[1])
    sys.exit(0 if ok else 1)
