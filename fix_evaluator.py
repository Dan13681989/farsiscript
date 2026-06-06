code = r'''
from parser import (
    PrintNode, ReadNode, IfNode, AssignNode, AssignIndexNode, BinOpNode, NumberNode, VarNode,
    StringNode, CallNode, FunctionNode, ReturnNode, RealNode,
    ArrayNode, IndexNode, DictNode, ForNode, WhileNode, BreakNode, ContinueNode, ImportNode,
    TryNode, ThrowNode, ClassNode, ThisNode, DotNode
)

class BreakException(Exception): pass
class ContinueException(Exception): pass

class Environment:
    def __init__(self, parent=None):
        self.vars = {}; self.parent = parent
    def get(self, name):
        if name in self.vars: return self.vars[name]
        if self.parent: return self.parent.get(name)
        return 0
    def set(self, name, value): self.vars[name] = value
    def set_local(self, name, value): self.vars[name] = value

class Function:
    def __init__(self, name, params, body, env):
        self.name=name; self.params=params; self.body=body; self.env=env

class Class:
    def __init__(self, name, body):
        self.name = name
        self.body = body

class Instance:
    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

def persian_to_english_digits(s):
    mapping = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٫': '.', '،': ''
    }
    return ''.join(mapping.get(ch, ch) for ch in s)

def evaluate(node, env, functions):
    if isinstance(node, NumberNode): return node.value
    elif isinstance(node, RealNode): return node.value
    elif isinstance(node, StringNode): return node.value
    elif isinstance(node, BinOpNode):
        left = evaluate(node.left, env, functions)
        right = evaluate(node.right, env, functions)
        if node.op == 'PLUS':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif node.op == 'MINUS': return left - right
        elif node.op == 'MUL': return left * right
        elif node.op == 'DIV': return left / right
        elif node.op == 'GT': return left > right
        elif node.op == 'LT': return left < right
        elif node.op == 'EQ': return left == right
        elif node.op == 'NEQ': return left != right
    elif isinstance(node, AssignNode):
        # Could be a simple assignment or this.field = value
        if '.' in node.name:
            # dot assignment: obj.attr = value
            parts = node.name.split('.')
            obj_name = parts[0]; attr = parts[1]
            if obj_name == 'this':
                obj = env.get('\u0627\u06cc\u0646')   # "این"
            else:
                obj = env.get(obj_name)
            if isinstance(obj, Instance):
                val = evaluate(node.expr, env, functions)
                obj.fields[attr] = val
                return val
            else:
                raise Exception("عملگر نقطه فقط روی اشیاء قابل استفاده است")
        else:
            val = evaluate(node.expr, env, functions)
            env.set_local(node.name, val)
            return val
    elif isinstance(node, AssignIndexNode):
        target = env.get(node.name)
        idx = evaluate(node.index, env, functions)
        val = evaluate(node.expr, env, functions)
        if isinstance(target, list):
            if not isinstance(idx, int): raise Exception("اندیس آرایه باید عدد صحیح باشد")
            if idx<0 or idx>=len(target): raise Exception(f"اندیس {idx} خارج از محدوده")
            target[idx] = val
            return val
        elif isinstance(target, dict):
            target[idx] = val
            return val
        else:
            raise Exception(f"متغیر '{node.name}' یک آرایه یا فرهنگ نیست")
    elif isinstance(node, VarNode):
        return env.get(node.name)
    elif isinstance(node, PrintNode):
        val = evaluate(node.expr, env, functions)
        if isinstance(val, float) and val.is_integer(): print(int(val))
        else: print(val)
        return val
    elif isinstance(node, ReadNode):
        inp = input()
        converted = persian_to_english_digits(inp)
        try:
            if '.' in converted: val = float(converted)
            else: val = int(converted)
        except ValueError: val = converted
        env.set_local(node.var_name, val)
        return val
    elif isinstance(node, IfNode):
        cond = evaluate(node.condition, env, functions)
        if cond: return evaluate(node.body, env, functions)
        elif node.else_body: return evaluate(node.else_body, env, functions)
        return None
    elif isinstance(node, WhileNode):
        res = None
        while evaluate(node.condition, env, functions):
            try: res = evaluate(node.body, env, functions)
            except BreakException: break
            except ContinueException: continue
        return res
    elif isinstance(node, ForNode):
        res = None
        if node.iter_expr is not None:
            arr = evaluate(node.iter_expr, env, functions)
            if isinstance(arr, str):
                for ch in arr:
                    env.set_local(node.var_name, ch)
                    try: res = evaluate(node.body, env, functions)
                    except BreakException: break
                    except ContinueException: continue
            elif isinstance(arr, list):
                for item in arr:
                    env.set_local(node.var_name, item)
                    try: res = evaluate(node.body, env, functions)
                    except BreakException: break
                    except ContinueException: continue
            elif isinstance(arr, dict):
                for key in arr:
                    env.set_local(node.var_name, key)
                    try: res = evaluate(node.body, env, functions)
                    except BreakException: break
                    except ContinueException: continue
            else:
                raise Exception("'برای با در' فقط روی آرایه، رشته یا فرهنگ پشتیبانی می‌شود")
        else:
            start = int(evaluate(node.start_expr, env, functions))
            end = int(evaluate(node.end_expr, env, functions))
            for i in range(start, end+1):
                env.set_local(node.var_name, i)
                try: res = evaluate(node.body, env, functions)
                except BreakException: break
                except ContinueException: continue
        return res
    elif isinstance(node, BreakNode): raise BreakException()
    elif isinstance(node, ContinueNode): raise ContinueException()
    elif isinstance(node, FunctionNode):
        functions[node.name] = Function(node.name, node.params, node.body, env)
        return None
    elif isinstance(node, CallNode):
        # Built-in functions
        if node.name == '\u0637\u0648\u0644':
            if len(node.args)!=1: raise Exception("طول یک آرگومان می‌پذیرد")
            arg = evaluate(node.args[0], env, functions)
            if isinstance(arg, (list, str, dict)): return len(arg)
            else: raise Exception("آرگومان طول باید آرایه، رشته یا فرهنگ باشد")
        elif node.name == '\u0646\u0648\u0639':
            if len(node.args)!=1: raise Exception("نوع یک آرگومان می‌پذیرد")
            arg = evaluate(node.args[0], env, functions)
            if isinstance(arg, bool): return "بول"
            elif isinstance(arg, int): return "عدد"
            elif isinstance(arg, float): return "اعشاری"
            elif isinstance(arg, str): return "رشته"
            elif isinstance(arg, list): return "آرایه"
            elif isinstance(arg, dict): return "فرهنگ"
            elif isinstance(arg, Instance): return "شیء"
            elif callable(arg): return "تابع"
            else: return "ناشناخته"
        elif node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u0641\u0627\u06cc\u0644':
            if len(node.args)!=1: raise Exception("خواندن_فایل یک آرگومان می‌پذیرد")
            path = evaluate(node.args[0], env, functions)
            with open(path, 'r', encoding='utf-8') as f: return f.read()
        elif node.name == '\u0646\u0648\u0634\u062a\u0646_\u0641\u0627\u06cc\u0644':
            if len(node.args)!=2: raise Exception("نوشتن_فایل دو آرگومان می‌پذیرد")
            path = evaluate(node.args[0], env, functions)
            content = evaluate(node.args[1], env, functions)
            with open(path, 'w', encoding='utf-8') as f: f.write(str(content))
            return None
        elif node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0639\u062f\u062f':
            if len(node.args)!=1: raise Exception("تبدیل_به_عدد یک آرگومان می‌پذیرد")
            arg = evaluate(node.args[0], env, functions)
            try:
                if isinstance(arg, str): return float(arg) if '.' in arg else int(arg)
                else: return float(arg) if '.' in str(arg) else int(arg)
            except: raise Exception("نمی‌توان به عدد تبدیل کرد")
        elif node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0631\u0634\u062a\u0647':
            if len(node.args)!=1: raise Exception("تبدیل_به_رشته یک آرگومان می‌پذیرد")
            arg = evaluate(node.args[0], env, functions)
            return str(arg)
        elif node.name == '\u062e\u0637\u0627_\u0628\u062f\u0647':
            if len(node.args)!=1: raise Exception("خطا_بده یک آرگومان می‌پذیرد")
            msg = evaluate(node.args[0], env, functions)
            raise Exception(str(msg))

        # Method call: if name contains a dot (obj.method), parse it
        if '.' in node.name:
            parts = node.name.split('.')
            if len(parts) != 2:
                raise Exception("نام تابع نامعتبر")
            obj_name, method = parts
            if obj_name == 'this':
                obj = env.get('\u0627\u06cc\u0646')
            else:
                obj = env.get(obj_name)
            if not isinstance(obj, Instance):
                raise Exception(f"'{obj_name}' یک شیء نیست")
            # Find the method in the class
            cls = obj.cls
            method_func = None
            for stmt in cls.body:
                if isinstance(stmt, FunctionNode) and stmt.name == method:
                    method_func = stmt
                    break
            if not method_func:
                raise Exception(f"متد '{method}' در کلاس '{cls.name}' وجود ندارد")
            # Create environment with 'این' bound to the instance
            call_env = Environment(env)
            call_env.set_local('\u0627\u06cc\u0646', obj)
            if len(node.args) != len(method_func.params):
                raise Exception(f"تعداد آرگومان‌های متد '{method}' صحیح نیست")
            for p, a in zip(method_func.params, node.args):
                call_env.set_local(p, evaluate(a, env, functions))
            res = None
            for stmt in method_func.body:
                res = evaluate(stmt, call_env, functions)
                if isinstance(stmt, ReturnNode): return res
            return res

        # Class constructor call
        cls = functions.get(node.name)
        if isinstance(cls, Class):
            inst = Instance(cls)
            constructor = None
            for stmt in cls.body:
                if isinstance(stmt, FunctionNode) and stmt.name == '\u062c\u062f\u06cc\u062f':
                    constructor = stmt
                    break
            if constructor:
                call_env = Environment(env)
                call_env.set_local('\u0627\u06cc\u0646', inst)
                for param, arg in zip(constructor.params, node.args):
                    call_env.set_local(param, evaluate(arg, env, functions))
                for stmt in constructor.body:
                    evaluate(stmt, call_env, functions)
            return inst

        # Regular function call
        func = functions.get(node.name)
        if not func: raise Exception(f"تابع '{node.name}' تعریف نشده است")
        if not isinstance(func, Function): raise Exception(f"'{node.name}' یک کلاس است، نمی‌توان مستقیماً فراخوانی کرد")
        call_env = Environment(func.env)
        if len(node.args) != len(func.params):
            raise Exception(f"تعداد آرگومان‌های تابع '{node.name}' صحیح نیست")
        for p,a in zip(func.params, node.args):
            call_env.set_local(p, evaluate(a, env, functions))
        res = None
        for stmt in func.body:
            res = evaluate(stmt, call_env, functions)
            if isinstance(stmt, ReturnNode): return res
        return res
    elif isinstance(node, ReturnNode):
        return evaluate(node.expr, env, functions)
    elif isinstance(node, ArrayNode):
        return [evaluate(e, env, functions) for e in node.elements]
    elif isinstance(node, DictNode):
        result = {}
        for key_node, value_node in node.pairs:
            k = evaluate(key_node, env, functions)
            v = evaluate(value_node, env, functions)
            result[k] = v
        return result
    elif isinstance(node, IndexNode):
        target = evaluate(node.array, env, functions)
        idx = evaluate(node.index, env, functions)
        if isinstance(target, (list, str)):
            if not isinstance(idx, int): raise Exception("اندیس باید عدد صحیح باشد")
            if idx<0 or idx>=len(target): raise Exception(f"اندیس {idx} خارج از محدوده")
            return target[idx]
        elif isinstance(target, dict):
            return target.get(idx, 0)
        else:
            raise Exception("شاخص فقط روی آرایه، رشته یا فرهنگ قابل استفاده است")
    elif isinstance(node, ImportNode):
        from tokenizer import Lexer
        from parser import Parser
        with open(node.filepath, 'r', encoding='utf-8') as f:
            imported_code = f.read()
        imported_lexer = Lexer(imported_code)
        imported_parser = Parser(imported_lexer.tokens)
        imported_ast = imported_parser.parse()
        for stmt in imported_ast:
            evaluate(stmt, env, functions)
        return None
    elif isinstance(node, TryNode):
        try:
            return evaluate(node.try_body, env, functions)
        except Exception as e:
            if node.catch_var:
                env.set_local(node.catch_var, str(e))
            return evaluate(node.catch_body, env, functions)
    elif isinstance(node, ThrowNode):
        msg = evaluate(node.message_expr, env, functions)
        raise Exception(str(msg))
    elif isinstance(node, ClassNode):
        cls = Class(node.name, node.body)
        functions[node.name] = cls
        return None
    elif isinstance(node, DotNode):
        obj = evaluate(node.obj, env, functions)
        if isinstance(obj, Instance):
            return obj.fields.get(node.attr, 0)
        else:
            raise Exception("عملگر نقطه فقط روی اشیاء قابل استفاده است")
    elif isinstance(node, ThisNode):
        return env.get('\u0627\u06cc\u0646')
    elif isinstance(node, list):
        res = None
        for stmt in node: res = evaluate(stmt, env, functions)
        return res
    else:
        raise Exception(f"نوع گره ناشناخته: {type(node)}")
'''

with open('evaluator.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('evaluator.py written successfully')
