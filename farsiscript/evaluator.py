import sys
import datetime
import math
import os
import time
import datetime
import random
import subprocess
from .parser import (
    PrintNode, ReadNode, IfNode, AssignNode, AssignIndexNode, BinOpNode, NumberNode, VarNode,
    StringNode, CallNode, FunctionNode, ReturnNode, RealNode,
    ArrayNode, IndexNode, DictNode, ForNode, WhileNode, BreakNode, ContinueNode, ImportNode,
    TryNode, ThrowNode, ClassNode, ThisNode, DotNode
)

def typeof(val):
    if isinstance(val, bool): return 'bool'
    if isinstance(val, int): return 'int'
    if isinstance(val, float): return 'float'
    if isinstance(val, str): return 'string'
    return type(val).__name__


def gregorian_to_jalali(g_y, g_m, g_d):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    gy = g_y - 1600
    gm = g_m - 1
    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    for i in range(gm):
        g_day_no += g_days_in_month[i]
    if gm > 1 and ((g_y % 4 == 0 and g_y % 100 != 0) or (g_y % 400 == 0)):
        g_day_no += 1
    g_day_no += g_d - 1
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    for i in range(11):
        if j_day_no >= j_days_in_month[i]:
            j_day_no -= j_days_in_month[i]
        else:
            break
    jm = i + 1
    jd = j_day_no + 1
    return jy, jm, jd

def jalali_date():
    now = datetime.datetime.now()
    jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
    return f"{jy}/{jm:02d}/{jd:02d}"

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
        self.name = name; self.body = body

class Instance:
    def __init__(self, cls):
        self.cls = cls; self.vars = Environment()

def evaluate(node, env, functions):
    if isinstance(node, NumberNode):
        return node.value
    elif isinstance(node, RealNode):
        return node.value
    elif isinstance(node, StringNode):
        return node.value
    elif isinstance(node, VarNode):
        return env.get(node.name)
    elif isinstance(node, AssignNode):
        val = evaluate(node.expr, env, functions)
        env.set(node.name, val)
        return val
    elif isinstance(node, AssignIndexNode):
        arr = evaluate(node.array, env, functions)
        idx = evaluate(node.index, env, functions)
        val = evaluate(node.expr, env, functions)
        arr[int(idx)] = val
        return val
    elif isinstance(node, BinOpNode):
        left = evaluate(node.left, env, functions)
        right = evaluate(node.right, env, functions)
        if node.op == '+': return left + right
        elif node.op == '-': return left - right
        elif node.op == '*': return left * right
        elif node.op == '/':
            if right == 0: raise Exception("تقسیم بر صفر")
            return left / right
        elif node.op == '%': return left % right
        elif node.op == '==': return left == right
        elif node.op == '!=': return left != right
        elif node.op == '<': return left < right
        elif node.op == '>': return left > right
        elif node.op == '<=': return left <= right
        elif node.op == '>=': return left >= right
        elif node.op == '&&': return left and right
        elif node.op == '||': return left or right
        elif node.op == '//': return int(left) // int(right)
    elif isinstance(node, PrintNode):
        val = evaluate(node.expr, env, functions)
        if isinstance(val, bool):
            print('صحیح' if val else 'غلط')
        else:
            print(val)
        return val
    elif isinstance(node, ReadNode):
        var = node.name
        inp = input()
        try:
            val = int(inp)
        except:
            try:
                val = float(inp)
            except:
                val = inp
        env.set(var, val)
        return val
    elif isinstance(node, IfNode):
        for cond, body in node.branches:
            if evaluate(cond, env, functions):
                for stmt in body:
                    evaluate(stmt, env, functions)
                return
        if node.else_body:
            for stmt in node.else_body:
                evaluate(stmt, env, functions)
    elif isinstance(node, ForNode):
        if node.iterator:
            iter_obj = evaluate(node.iterable, env, functions)
            if isinstance(iter_obj, str):
                for ch in iter_obj:
                    env.set_local(node.iterator, ch)
                    for stmt in node.body:
                        evaluate(stmt, env, functions)
            elif isinstance(iter_obj, dict):
                for key, val in iter_obj.items():
                    env.set_local(node.iterator, (key, val))
                    for stmt in node.body:
                        evaluate(stmt, env, functions)
            else:
                for item in iter_obj:
                    env.set_local(node.iterator, item)
                    for stmt in node.body:
                        evaluate(stmt, env, functions)
        else:
            start = evaluate(node.start, env, functions)
            end = evaluate(node.end, env, functions)
            step = evaluate(node.step, env, functions) if node.step else 1
            i = start
            while i <= end:
                env.set_local(node.var_name, i)
                for stmt in node.body:
                    evaluate(stmt, env, functions)
                i += step
    elif isinstance(node, WhileNode):
        while evaluate(node.cond, env, functions):
            for stmt in node.body:
                evaluate(stmt, env, functions)
    elif isinstance(node, BreakNode):
        raise BreakException()
    elif isinstance(node, ContinueNode):
        raise ContinueException()
    elif isinstance(node, ReturnNode):
        if node.expr:
            return evaluate(node.expr, env, functions)
        return None
    elif isinstance(node, FunctionNode):
        func = Function(node.name, node.params, node.body, env)
        functions[node.name] = func
        return func
    elif isinstance(node, CallNode):
        args = [evaluate(a, env, functions) for a in node.args]
        # --- Built-in functions (standard library) ---
        if node.name == 'ریشه_دوم':
            return math.sqrt(args[0])
        elif node.name == 'قدر_مطلق':
            return abs(args[0])
        elif node.name == 'سقف':
            return math.ceil(args[0])
        elif node.name == 'کف':
            return math.floor(args[0])
        elif node.name == 'طول_رشته':
            return len(args[0])
        elif node.name == 'بزرگکن':
            return args[0].upper()
        elif node.name == 'کوچککن':
            return args[0].lower()
        elif node.name == 'زمان_اکنون':
            return time.ctime()
        elif node.name == 'عدد_تصادفی':
            return random.randint(int(args[0]), int(args[1]))
        elif node.name == '\u0627\u062c\u0631\u0627':
            import subprocess
            cmd = args[0]
            return subprocess.getoutput(cmd)
        # --- User-defined functions ---
        elif node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u0641\u0627\u06cc\u0644':
            with open(args[0], 'r', encoding='utf-8') as f:
                return f.read()
        elif node.name == '\u0646\u0648\u0634\u062a\u0646_\u0641\u0627\u06cc\u0644':
            with open(args[0], 'w', encoding='utf-8') as f:
                f.write(args[1])
            return 1
        elif node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u0641\u0627\u06cc\u0644':
            with open(args[0], 'r', encoding='utf-8') as f:
                return f.read()
        elif node.name == '\u0646\u0648\u0634\u062a\u0646_\u0641\u0627\u06cc\u0644':
            with open(args[0], 'w', encoding='utf-8') as f:
                f.write(args[1])
            return 1
        elif node.name == '\u062a\u0627\u0631\u06cc\u062e_\u0634\u0645\u0633\u06cc':
            return jalali_date()
        elif node.name == '\u0628\u0631\u0639\u06a9\u0633_\u0631\u0634\u062a\u0647':
            return args[0][::-1]
        elif node.name == '\u062a\u0627\u0631\u06cc\u062e_\u0627\u0645\u0631\u0648\u0632':
            import datetime
            return datetime.date.today().isoformat()
        elif node.name == '\u062d\u0630\u0641_\u0641\u0627\u0635\u0644\u0647':
            return args[0].strip()
        elif node.name == '\u062a\u0648\u0627\u0646':
            return args[0] ** args[1]
        elif node.name == '\u0633\u06cc\u0646\u0648\u0633':
            import math
            return math.sin(args[0])
        elif node.name == '\u06a9\u0633\u06cc\u0646\u0648\u0633':
            import math
            return math.cos(args[0])
        elif node.name == '\u0644\u06af\u0627\u0631\u06cc\u062a\u0645':
            import math
            return math.log(args[0])
        elif node.name == '\u0645\u0631\u062a\u0628_\u0633\u0627\u0632\u06cc':
            return sorted(args[0])
        elif node.name == '\u0644\u06cc\u0633\u062a_\u0641\u0627\u06cc\u0644_\u0647\u0627':
            import os
            return '\n'.join(os.listdir(args[0] if args else '.'))
        elif node.name == '\u062d\u0630\u0641_\u0641\u0627\u06cc\u0644':
            import os
            os.remove(args[0])
            return 1
        elif node.name == '\u062f\u0631\u06cc\u0627\u0641\u062a_\u0627\u0632_\u0648\u0628':
            import urllib.request
            try:
                with urllib.request.urlopen(args[0]) as resp:
                    return resp.read().decode('utf-8')
            except Exception as e:
                return f'خطا: {e}'
        elif node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u062c\u06cc\u0633\u0648\u0646':
            import json
            return json.loads(args[0])
        elif node.name == '\u0646\u0648\u0634\u062a\u0646_\u062c\u06cc\u0633\u0648\u0646':
            import json
            return json.dumps(args[0], ensure_ascii=False)
        func = functions.get(node.name)
        if not func: raise Exception(f"تابع '{node.name}' تعریف نشده است")
        if not isinstance(func, Function): raise Exception(f"'{node.name}' یک کلاس است، نمی‌توان مستقیماً فراخوانی کرد")
        call_env = Environment(func.env)
        if len(args) != len(func.params):
            raise Exception(f"تعداد آرگومان‌های تابع '{node.name}' صحیح نیست")
        for p, a in zip(func.params, args):
            call_env.set_local(p, a)
        res = None
        for stmt in func.body:
            res = evaluate(stmt, call_env, functions)
        return res
    elif isinstance(node, ArrayNode):
        return [evaluate(e, env, functions) for e in node.elements]
    elif isinstance(node, IndexNode):
        obj = evaluate(node.object, env, functions)
        idx = evaluate(node.index, env, functions)
        return obj[int(idx)]
    elif isinstance(node, DictNode):
        d = {}
        for k, v in node.items:
            d[evaluate(k, env, functions)] = evaluate(v, env, functions)
        return d
    elif isinstance(node, DotNode):
        obj = evaluate(node.object, env, functions)
        attr = node.attr
        if isinstance(obj, Instance):
            if attr in obj.vars.vars:
                return obj.vars.vars[attr]
            # Look for method in class
            for stmt in obj.cls.body:
                if isinstance(stmt, FunctionNode) and stmt.name == attr:
                    method = Function(attr, stmt.params, stmt.body, obj.vars)
                    # bind 'this' to the instance
                    method.env.set_local('این', obj)
                    functions[attr] = method
                    return method
            raise Exception(f"ویژگی '{attr}' در شیء وجود ندارد")
        elif isinstance(obj, dict):
            return obj.get(attr, 0)
        elif isinstance(obj, str) and attr == 'طول':
            return len(obj)
        else:
            raise Exception(f"نوع داده از عملیات نقطه پشتیبانی نمی‌کند")
    elif isinstance(node, ImportNode):
        with open(node.filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        from .tokenizer import Lexer
        from .parser import Parser
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        for stmt in ast:
            evaluate(stmt, env, functions)
    elif isinstance(node, TryNode):
        try:
            for stmt in node.try_body:
                evaluate(stmt, env, functions)
        except Exception as e:
            if node.catch_var:
                env.set_local(node.catch_var, str(e))
            for stmt in node.catch_body:
                evaluate(stmt, env, functions)
    elif isinstance(node, ThrowNode):
        msg = evaluate(node.expr, env, functions) if node.expr else "خطای ناشناخته"
        raise Exception(msg)
    elif isinstance(node, ClassNode):
        cls = Class(node.name, node.body)
        functions[node.name] = cls
        return cls
    elif isinstance(node, ThisNode):
        return env.get('این')
    else:
        raise Exception(f"نوع گره ناشناخته: {type(node).__name__}")
