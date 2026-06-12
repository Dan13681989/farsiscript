import sys
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
        elif node.name == 'اجرا':
            return os.system(args[0])
        elif node.name == 'فرمت_تاریخ':
            return time.strftime(args[0], time.localtime())
        elif node.name == 'تکرار_رشته':
            return args[0] * int(args[1])
        elif node.name == 'طول_آرایه':
            return len(args[0])
        elif node.name == 'نوع':
            return typeof(args[0])
        # --- User-defined functions ---
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
        with open(node.file, 'r', encoding='utf-8') as f:
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
