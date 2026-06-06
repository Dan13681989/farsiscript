import os

code = r'''
import sys, subprocess
from tokenizer import Lexer
from parser import (
    Parser, NumberNode, RealNode, StringNode, BinOpNode, AssignNode,
    VarNode, PrintNode, ReadNode, IfNode, WhileNode, ForNode, CallNode,
    ArrayNode, IndexNode, DictNode, FunctionNode, ReturnNode, BreakNode, ContinueNode,
    AssignIndexNode, ImportNode, TryNode, ThrowNode, ClassNode, ThisNode, DotNode
)

class Function:
    pass

OP_MAP = {'PLUS':'+','MINUS':'-','MUL':'*','DIV':'/','GT':'>','LT':'<','EQ':'==','NEQ':'!='}

def safe_name(name):
    return name.replace('.', '_')

def compile_to_c(code, output_c_file):
    lexer = Lexer(code); tokens = lexer.tokens
    parser = Parser(tokens); ast = parser.parse()

    functions = {}; statements = []
    classes = {}
    for s in ast:
        if isinstance(s, FunctionNode): functions[s.name] = s
        elif isinstance(s, ClassNode):
            classes[s.name] = s
            for stmt in s.body:
                if isinstance(stmt, FunctionNode):
                    safe_fn = safe_name(f'{s.name}.{stmt.name}')
                    functions[safe_fn] = stmt
        else: statements.append(s)

    for stmt in statements:
        if isinstance(stmt, ImportNode):
            with open(stmt.filepath, 'r', encoding='utf-8') as f:
                imported_code = f.read()
            imported_lexer = Lexer(imported_code)
            imported_parser = Parser(imported_lexer.tokens)
            imported_ast = imported_parser.parse()
            for s in imported_ast:
                if isinstance(s, FunctionNode):
                    functions[s.name] = s
                elif isinstance(s, ClassNode):
                    classes[s.name] = s
                    for stmt in s.body:
                        if isinstance(stmt, FunctionNode):
                            functions[safe_name(f'{s.name}.{stmt.name}')] = stmt

    var_info = {}; param_types = {}

    def infer_type(node, func_name=None):
        if isinstance(node, StringNode): return 'string'
        if isinstance(node, (NumberNode, RealNode)): return 'double'
        if isinstance(node, BinOpNode):
            l = infer_type(node.left, func_name); r = infer_type(node.right, func_name)
            if node.op == 'PLUS' and (l=='string' or r=='string'): return 'string'
            return 'double'
        if isinstance(node, VarNode):
            if func_name and (func_name, node.name) in param_types: return param_types[(func_name, node.name)]
            info = var_info.get(node.name, {})
            if info.get('type') == 'class_obj':
                return f'struct_{info["class_name"]}*'
            return info.get('type', 'double')
        if isinstance(node, CallNode):
            if node.name == '\u0637\u0648\u0644': return 'double'
            if node.name == '\u0646\u0648\u0639': return 'string'
            if node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u0641\u0627\u06cc\u0644': return 'string'
            if node.name == '\u0646\u0648\u0634\u062a\u0646_\u0641\u0627\u06cc\u0644': return 'void'
            if node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0639\u062f\u062f': return 'double'
            if node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0631\u0634\u062a\u0647': return 'string'
            if node.name == '\u062e\u0637\u0627_\u0628\u062f\u0647': return 'void'
            if node.name in classes: return f'struct_{node.name}*'
            if '.' in node.name: return 'double'
            return 'double'
        if isinstance(node, IndexNode):
            if isinstance(node.array, VarNode) and var_info.get(node.array.name, {}).get('type') == 'dict':
                return 'string'
            return 'double'
        if isinstance(node, ArrayNode): return 'array'
        if isinstance(node, DictNode): return 'dict'
        if isinstance(node, DotNode): return 'double'
        if isinstance(node, ThisNode): return 'double'
        return 'double'

    def collect_globals(node):
        if isinstance(node, AssignNode):
            t = infer_type(node.expr)
            if t == 'array':
                size = len(node.expr.elements)
                var_info[node.name] = {'type': 'array', 'size': size}
            elif t == 'dict':
                var_info[node.name] = {'type': 'dict'}
            elif t.startswith('struct_'):
                var_info[node.name] = {'type': 'class_obj', 'class_name': t.replace('struct_','').replace('*','')}
            else:
                var_info[node.name] = {'type': t}
        elif isinstance(node, ReadNode):
            if node.var_name not in var_info:
                var_info[node.var_name] = {'type': 'double'}
        elif isinstance(node, list):
            for c in node: collect_globals(c)
        elif isinstance(node, (IfNode, WhileNode, ForNode, TryNode)):
            if hasattr(node, 'try_body'):
                collect_globals(node.try_body)
                if node.catch_var:
                    var_info[node.catch_var] = {'type': 'string'}
                collect_globals(node.catch_body)
            else:
                collect_globals(node.body)
                if hasattr(node, 'else_body') and node.else_body: collect_globals(node.else_body)
        elif isinstance(node, ClassNode):
            pass
        elif isinstance(node, ImportNode):
            with open(node.filepath, 'r', encoding='utf-8') as f:
                imported_code = f.read()
            imported_lexer = Lexer(imported_code)
            imported_parser = Parser(imported_lexer.tokens)
            imported_ast = imported_parser.parse()
            for s in imported_ast:
                collect_globals(s)
    for s in statements: collect_globals(s)

    def find_calls(node, func_name=None):
        if isinstance(node, CallNode) and node.name in functions:
            f = functions[node.name]
            if isinstance(f, Function):
                for p,a in zip(f.params, node.args):
                    t = infer_type(a, func_name)
                    key = (node.name, p)
                    if key not in param_types: param_types[key] = t
                    elif param_types[key] != t: param_types[key] = 'string'
        elif isinstance(node, list):
            for c in node: find_calls(c, func_name)
        elif isinstance(node, (IfNode, WhileNode, ForNode)):
            find_calls(node.body, func_name)
            if hasattr(node, 'else_body') and node.else_body: find_calls(node.else_body, func_name)
        elif isinstance(node, TryNode):
            find_calls(node.try_body, func_name)
            find_calls(node.catch_body, func_name)
        elif isinstance(node, ClassNode):
            pass
        elif isinstance(node, ImportNode):
            with open(node.filepath, 'r', encoding='utf-8') as f:
                imported_code = f.read()
            imported_lexer = Lexer(imported_code)
            imported_parser = Parser(imported_lexer.tokens)
            imported_ast = imported_parser.parse()
            for s in imported_ast:
                find_calls(s, func_name)
    for s in statements: find_calls(s)
    for fnode in functions.values():
        if isinstance(fnode, Function):
            find_calls(fnode.body, fnode.name)
    for fn, fnode in functions.items():
        if isinstance(fnode, Function):
            for p in fnode.params:
                if (fn, p) not in param_types: param_types[(fn, p)] = 'double'

    def c_name(name, func=None):
        if func and (func, name) in param_types: return name
        return f'var_{name}'

    c_code = '#include <stdio.h>\n#include <string.h>\n#include <stdlib.h>\n#include <stdint.h>\n#include <setjmp.h>\n#include <signal.h>\n\n'

    # ---------- forward declarations ----------
    declared = set()
    def declare_func(name, ret_type, params):
        if name not in declared:
            c_code.append(f'{ret_type} {name}({", ".join(params)});\n')
            declared.add(name)

    # We'll collect all user functions and add prototypes after helpers.
    # But we need to know return types and parameters before we build the full code.
    # So we'll build prototypes in a second pass.  Instead, we'll generate the whole code with
    # definitions and then prepend prototypes by analyzing the emitted code?  Simplest:
    # after generating all code, we extract function signatures and insert prototypes.
    # We'll do that by splitting the generated code.
    # Let's store the function declarations we're going to emit in a list,
    # then later add them before main.
    forward_decls = []

    # ... (helper structs)

    c_code += (
        'typedef struct DictEntry {\n'
        '    char* key;\n'
        '    char* value;\n'
        '    struct DictEntry* next;\n'
        '} DictEntry;\n\n'
        'typedef struct {\n'
        '    DictEntry* head;\n'
        '} Dict;\n\n'
        'Dict* dict_create() {\n'
        '    Dict* d = (Dict*)malloc(sizeof(Dict));\n'
        '    d->head = NULL;\n'
        '    return d;\n'
        '}\n\n'
        'void dict_set_str(Dict* d, const char* key, const char* value) {\n'
        '    DictEntry* e = d->head;\n'
        '    while (e) {\n'
        '        if (strcmp(e->key, key) == 0) {\n'
        '            free(e->value);\n'
        '            e->value = strdup(value);\n'
        '            return;\n'
        '        }\n'
        '        e = e->next;\n'
        '    }\n'
        '    e = (DictEntry*)malloc(sizeof(DictEntry));\n'
        '    e->key = strdup(key);\n'
        '    e->value = strdup(value);\n'
        '    e->next = d->head;\n'
        '    d->head = e;\n'
        '}\n\n'
        'void dict_set_num(Dict* d, const char* key, double value) {\n'
        '    char buf[64];\n'
        '    sprintf(buf, "%g", value);\n'
        '    dict_set_str(d, key, buf);\n'
        '}\n\n'
        'char* dict_get(Dict* d, const char* key) {\n'
        '    DictEntry* e = d->head;\n'
        '    while (e) {\n'
        '        if (strcmp(e->key, key) == 0) return e->value;\n'
        '        e = e->next;\n'
        '    }\n'
        '    return "0";\n'
        '}\n\n'
        'int dict_length(Dict* d) {\n'
        '    int len = 0;\n'
        '    DictEntry* e = d->head;\n'
        '    while (e) { len++; e = e->next; }\n'
        '    return len;\n'
        '}\n\n'
        'void dict_free(Dict* d) {\n'
        '    DictEntry* e = d->head;\n'
        '    while (e) {\n'
        '        DictEntry* next = e->next;\n'
        '        free(e->key);\n'
        '        free(e->value);\n'
        '        free(e);\n'
        '        e = next;\n'
        '    }\n'
        '    free(d);\n'
        '}\n\n'
    )

    for cls_name, cls_node in classes.items():
        fields = set()
        for stmt in cls_node.body:
            if isinstance(stmt, FunctionNode) and stmt.name == '\u062c\u062f\u06cc\u062f':
                for p in stmt.params:
                    fields.add(p)
        c_code += f'typedef struct {{\n'
        for field in fields:
            c_code += f'    double {field};\n'
        c_code += f'}} struct_{cls_name};\n\n'

    for v, info in var_info.items():
        if info['type'] == 'string':
            c_code += f'char var_{v}[256];\n'
        elif info['type'] == 'array':
            c_code += f'double var_{v}[{info["size"]}];\n'
        elif info['type'] == 'dict':
            c_code += f'Dict* var_{v};\n'
        elif info['type'] == 'class_obj':
            c_code += f'struct_{info["class_name"]}* var_{v};\n'
        else:
            c_code += f'double var_{v};\n'
    c_code += '\n'

    c_code += (
        'void str_concat_ss(char*d,const char*a,const char*b){strcpy(d,a);strcat(d,b);}\n'
        'void str_concat_sd(char*d,const char*a,double b){char tmp[64];sprintf(tmp,"%g",b);strcpy(d,a);strcat(d,tmp);}\n'
        'void str_concat_ds(char*d,double a,const char*b){char tmp[64];sprintf(tmp,"%g",a);strcpy(d,tmp);strcat(d,b);}\n'
        'char* read_file(const char* path){FILE *f=fopen(path,"r");if(!f)return "";fseek(f,0,SEEK_END);long len=ftell(f);fseek(f,0,SEEK_SET);char* buf=malloc(len+1);fread(buf,1,len,f);buf[len]=0;fclose(f);return buf;}\n'
        'void write_file(const char* path, const char* content){FILE *f=fopen(path,"w");if(f){fputs(content,f);fclose(f);}}\n'
        'int is_persian_digit(unsigned char* s, int* value) {\n'
        '    if (s[0] == 0xDB && s[1] >= 0xB0 && s[1] <= 0xB9) {\n'
        '        *value = s[1] - 0xB0;\n'
        '        return 2;\n'
        '    }\n'
        '    if (s[0] == 0xD9 && s[1] == 0xAB) {\n'
        '        *value = -2;\n'
        '        return 2;\n'
        '    }\n'
        '    return 0;\n'
        '}\n'
        'void convert_persian_digits(char* dest, const char* src) {\n'
        '    while (*src) {\n'
        '        int value;\n'
        '        int len = is_persian_digit((unsigned char*)src, &value);\n'
        '        if (len > 0) {\n'
        '            if (value == -2) {\n'
        '                *dest++ = \'.\';\n'
        '            } else {\n'
        '                *dest++ = \'0\' + value;\n'
        '            }\n'
        '            src += len;\n'
        '        } else {\n'
        '            *dest++ = *src++;\n'
        '        }\n'
        '    }\n'
        '    *dest = 0;\n'
        '}\n'
        'void safe_scanf_double(double* var) {\n'
        '    char input[256];\n'
        '    scanf("%255s", input);\n'
        '    char converted[256];\n'
        '    convert_persian_digits(converted, input);\n'
        '    *var = atof(converted);\n'
        '}\n\n'
        'jmp_buf __try_buf;\n'
        'char __try_error[256];\n'
        'void __try_signal_handler(int sig) {\n'
        '    if (sig == SIGFPE) {\n'
        '        strcpy(__try_error, "division by zero");\n'
        '    } else {\n'
        '        strcpy(__try_error, "unknown error");\n'
        '    }\n'
        '    longjmp(__try_buf, 1);\n'
        '}\n\n'
    )

    temp_cnt = [0]
    def new_temp(prefix='t'): temp_cnt[0]+=1; return f'{prefix}_{temp_cnt[0]}'

    def is_dict_var(name, func_name=None):
        if func_name and (func_name, name) in param_types:
            return param_types[(func_name, name)] == 'dict'
        return var_info.get(name, {}).get('type') == 'dict'

    def gen_expr(node, func_name, local_vars, decls):
        if isinstance(node, NumberNode): return str(node.value)
        if isinstance(node, RealNode): return str(node.value)
        if isinstance(node, StringNode): return '"'+node.value+'"'
        if isinstance(node, BinOpNode):
            left = gen_expr(node.left, func_name, local_vars, decls)
            right = gen_expr(node.right, func_name, local_vars, decls)
            lt = infer_type(node.left, func_name); rt = infer_type(node.right, func_name)
            if node.op == 'PLUS' and (lt=='string' or rt=='string'):
                tmp = new_temp('s')
                if lt=='string' and rt=='string':
                    decls.append(f'char {tmp}[512];')
                    decls.append(f'str_concat_ss({tmp}, {left}, {right});')
                elif lt=='string' and rt=='double':
                    decls.append(f'char {tmp}[512];')
                    decls.append(f'str_concat_sd({tmp}, {left}, {right});')
                elif lt=='double' and rt=='string':
                    decls.append(f'char {tmp}[512];')
                    decls.append(f'str_concat_ds({tmp}, {left}, {right});')
                else:
                    decls.append(f'char {tmp}[512];')
                    decls.append(f'str_concat_ss({tmp}, {left}, {right});')
                return tmp
            else:
                op = OP_MAP.get(node.op, node.op)
                return f'({left} {op} {right})'
        if isinstance(node, VarNode):
            return c_name(node.name, func_name)
        if isinstance(node, AssignNode):
            return gen_expr(node.expr, func_name, local_vars, decls)
        if isinstance(node, CallNode):
            if node.name == '\u0637\u0648\u0644':
                arg = node.args[0]
                if isinstance(arg, VarNode) and is_dict_var(arg.name, func_name):
                    return f'dict_length({c_name(arg.name, func_name)})'
                return f'strlen({gen_expr(arg, func_name, local_vars, decls)})'
            if node.name == '\u0646\u0648\u0639':
                arg = node.args[0]
                if isinstance(arg, StringNode): return '"\u0631\u0634\u062a\u0647"'
                if isinstance(arg, NumberNode): return '"\u0639\u062f\u062f"'
                if isinstance(arg, RealNode): return '"\u0627\u0639\u0634\u0627\u0631\u06cc"'
                if isinstance(arg, ArrayNode): return '"\u0622\u0631\u0627\u06cc\u0647"'
                if isinstance(arg, DictNode): return '"\u0641\u0631\u0647\u0646\u06af"'
                if isinstance(arg, VarNode):
                    vtype = var_info.get(arg.name, {}).get('type', 'double')
                    if vtype == 'string': return '"\u0631\u0634\u062a\u0647"'
                    elif vtype == 'array': return '"\u0622\u0631\u0627\u06cc\u0647"'
                    elif vtype == 'dict': return '"\u0641\u0631\u0647\u0646\u06af"'
                    else: return '"\u0639\u062f\u062f"'
                return '"(unknown)"'
            if node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u0641\u0627\u06cc\u0644':
                path = gen_expr(node.args[0], func_name, local_vars, decls)
                return f'read_file({path})'
            if node.name == '\u0646\u0648\u0634\u062a\u0646_\u0641\u0627\u06cc\u0644':
                path = gen_expr(node.args[0], func_name, local_vars, decls)
                content = gen_expr(node.args[1], func_name, local_vars, decls)
                return f'write_file({path}, {content})'
            if node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0639\u062f\u062f':
                arg = gen_expr(node.args[0], func_name, local_vars, decls)
                return f'atof({arg})'
            if node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0631\u0634\u062a\u0647':
                arg = gen_expr(node.args[0], func_name, local_vars, decls)
                return arg
            if node.name == '\u062e\u0637\u0627_\u0628\u062f\u0647':
                arg = gen_expr(node.args[0], func_name, local_vars, decls)
                return arg
            # method call
            if '.' in node.name:
                parts = node.name.split('.')
                obj_name = parts[0]; method = parts[1]
                obj_var = c_name(obj_name, func_name)
                cls_name = var_info[obj_name]['class_name']
                safe_fn = f'{cls_name}_{method}'
                if node.args:
                    args = ', '.join(gen_expr(a, func_name, local_vars, decls) for a in node.args)
                    return f'{safe_fn}({obj_var}, {args})'
                else:
                    return f'{safe_fn}({obj_var})'
            args = ', '.join(gen_expr(a, func_name, local_vars, decls) for a in node.args)
            return f'{node.name}({args})'
        if isinstance(node, ReturnNode):
            return gen_expr(node.expr, func_name, local_vars, decls)
        if isinstance(node, IfNode):
            cond = gen_expr(node.condition, func_name, local_vars, decls)
            body_lines = gen_block(node.body if isinstance(node.body,list) else [node.body], func_name, local_vars, decls)
            else_part = ''
            if node.else_body:
                else_lines = gen_block(node.else_body if isinstance(node.else_body,list) else [node.else_body], func_name, local_vars, decls)
                else_part = f' else {{\n{else_lines}\n}}'
            return f'if ({cond}) {{\n{body_lines}\n}}{else_part}'
        if isinstance(node, ArrayNode): return ''
        if isinstance(node, DictNode):
            tmp_dict = new_temp('dict')
            decls.append(f'Dict* {tmp_dict} = dict_create();')
            for key_node, value_node in node.pairs:
                key_str = gen_expr(key_node, func_name, local_vars, decls)
                val_str = gen_expr(value_node, func_name, local_vars, decls)
                val_type = infer_type(value_node, func_name)
                if val_type == 'string':
                    decls.append(f'dict_set_str({tmp_dict}, {key_str}, {val_str});')
                else:
                    decls.append(f'dict_set_num({tmp_dict}, {key_str}, {val_str});')
            return tmp_dict
        if isinstance(node, IndexNode):
            arr = node.array
            if isinstance(arr, VarNode) and is_dict_var(arr.name, func_name):
                key = gen_expr(node.index, func_name, local_vars, decls)
                return f'dict_get({c_name(arr.name, func_name)}, {key})'
            else:
                arr_str = gen_expr(arr, func_name, local_vars, decls)
                idx = gen_expr(node.index, func_name, local_vars, decls)
                return f'{arr_str}[{idx}]'
        if isinstance(node, DotNode):
            obj = gen_expr(node.obj, func_name, local_vars, decls)
            return f'{obj}->{node.attr}'
        if isinstance(node, ThisNode):
            return 'self'
        return '0'

    def gen_stmt(node, func_name, local_vars, decls):
        if isinstance(node, PrintNode):
            expr = node.expr
            typ = infer_type(expr, func_name)
            e = gen_expr(expr, func_name, local_vars, decls)
            if isinstance(expr, StringNode): return f'printf("{expr.value}\\n");'
            elif typ == 'string':
                return f'printf("%s\\n", {e});'
            elif isinstance(expr, CallNode) and expr.name == '\u0637\u0648\u0644':
                return f'printf("%d\\n", {e});'
            elif typ == 'double':
                return f'printf("%g\\n", {e});'
            else:
                return f'printf("%d\\n", {e});'
        if isinstance(node, AssignNode):
            if isinstance(node.expr, CallNode) and node.expr.name in classes:
                cls_name = node.expr.name
                obj_var = new_temp('obj')
                decls.append(f'struct_{cls_name}* {obj_var} = malloc(sizeof(struct_{cls_name}));')
                constr_name = f'{cls_name}_\u062c\u062f\u06cc\u062f'
                constr = functions.get(constr_name)
                if constr:
                    if node.expr.args:
                        args = ', '.join(gen_expr(a, func_name, local_vars, decls) for a in node.expr.args)
                        decls.append(f'{constr_name}({obj_var}, {args});')
                    else:
                        decls.append(f'{constr_name}({obj_var});')
                decls.append(f'{c_name(node.name, func_name)} = {obj_var};')
                return ''
            if isinstance(node.expr, DictNode):
                target = c_name(node.name, func_name)
                decls.append(f'{target} = dict_create();')
                for key_node, value_node in node.expr.pairs:
                    key_str = gen_expr(key_node, func_name, local_vars, decls)
                    val_str = gen_expr(value_node, func_name, local_vars, decls)
                    val_type = infer_type(value_node, func_name)
                    if val_type == 'string':
                        decls.append(f'dict_set_str({target}, {key_str}, {val_str});')
                    else:
                        decls.append(f'dict_set_num({target}, {key_str}, {val_str});')
                return ''
            if is_dict_var(node.name, func_name):
                val = gen_expr(node.expr, func_name, local_vars, decls)
                return f'{c_name(node.name, func_name)} = {val};'
            val = gen_expr(node, func_name, local_vars, decls)
            if isinstance(node.expr, ArrayNode):
                arr_var = c_name(node.name, func_name)
                elems = node.expr.elements
                idx = new_temp('i')
                decls.append(f'int {idx};')
                assignments = []
                for i, elem in enumerate(elems):
                    assignments.append(f'{arr_var}[{i}] = {gen_expr(elem, func_name, local_vars, decls)};')
                decls.append(f'for({idx}=0; {idx}<{len(elems)}; ++{idx}) {{')
                for a in assignments: decls.append(f'    {a}')
                decls.append('}')
                return ''
            target = c_name(node.name, func_name)
            if var_info.get(node.name, {}).get('type') == 'string' or \
               (func_name and param_types.get((func_name, node.name)) == 'string'):
                return f'strcpy({target}, {val});'
            else:
                return f'{target} = {val};'
        if isinstance(node, AssignIndexNode):
            if is_dict_var(node.name, func_name):
                target = c_name(node.name, func_name)
                key = gen_expr(node.index, func_name, local_vars, decls)
                val = gen_expr(node.expr, func_name, local_vars, decls)
                val_type = infer_type(node.expr, func_name)
                if val_type == 'string':
                    return f'dict_set_str({target}, {key}, {val});'
                else:
                    return f'dict_set_num({target}, {key}, {val});'
            else:
                target = c_name(node.name, func_name)
                idx = gen_expr(node.index, func_name, local_vars, decls)
                val = gen_expr(node.expr, func_name, local_vars, decls)
                return f'{target}[(int){idx}] = {val};'
        if isinstance(node, ReadNode):
            target = c_name(node.var_name, func_name)
            return f'safe_scanf_double(&{target});'
        if isinstance(node, IfNode): return gen_expr(node, func_name, local_vars, decls)
        if isinstance(node, WhileNode):
            cond = gen_expr(node.condition, func_name, local_vars, decls)
            body = gen_block(node.body if isinstance(node.body,list) else [node.body], func_name, local_vars, decls)
            return f'while ({cond}) {{\n{body}\n}}'
        if isinstance(node, ForNode):
            if node.iter_expr is not None:
                expr_type = infer_type(node.iter_expr, func_name)
                arr_var = gen_expr(node.iter_expr, func_name, local_vars, decls)
                loop_var = c_name(node.var_name, func_name)
                decls.append(f'char {loop_var}[256];')
                var_info[node.var_name] = {'type': 'string'}
                idx = new_temp('i')
                if expr_type == 'string':
                    len_var = new_temp('len')
                    decls.append(f'int {len_var} = strlen({arr_var});')
                    decls.append(f'int {idx};')
                    body = gen_block(node.body if isinstance(node.body,list) else [node.body], func_name, local_vars, decls)
                    return f'for ({idx}=0; {idx}<{len_var}; ++{idx}) {{\n    {loop_var} = {arr_var}[{idx}];\n{body}\n}}'
                elif isinstance(node.iter_expr, VarNode):
                    arr_name = node.iter_expr.name
                    arr_info = var_info.get(arr_name, {})
                    if arr_info.get('type') == 'array':
                        size = arr_info['size']
                        decls.append(f'int {idx};')
                        body = gen_block(node.body if isinstance(node.body,list) else [node.body], func_name, local_vars, decls)
                        return f'for ({idx}=0; {idx}<{size}; ++{idx}) {{\n    {loop_var} = {arr_var}[{idx}];\n{body}\n}}'
                    elif arr_info.get('type') == 'dict':
                        entry_ptr = new_temp('entry')
                        decls.append(f'DictEntry* {entry_ptr} = {arr_var}->head;')
                        decls_len = len(decls)
                        body = gen_block(node.body if isinstance(node.body,list) else [node.body], func_name, local_vars, decls)
                        new_decls = decls[decls_len:]
                        del decls[decls_len:]
                        inner = ''
                        inner += f'    strcpy({loop_var}, {entry_ptr}->key);\n'
                        if new_decls:
                            inner += '\n'.join('    '+d for d in new_decls) + '\n'
                        inner += body + '\n'
                        inner += f'    {entry_ptr} = {entry_ptr}->next;\n'
                        return f'while ({entry_ptr} != NULL) {{\n{inner}}}'
                return '/* not supported */'
            else:
                var = node.var_name
                start = gen_expr(node.start_expr, func_name, local_vars, decls)
                end = gen_expr(node.end_expr, func_name, local_vars, decls)
                c_var = c_name(var, func_name)
                decls.append(f'double {c_var};')
                body = gen_block(node.body if isinstance(node.body,list) else [node.body], func_name, local_vars, decls)
                return f'for ({c_var}={start}; {c_var}<={end}; ++{c_var}) {{\n{body}\n}}'
        if isinstance(node, BreakNode): return 'break;'
        if isinstance(node, ContinueNode): return 'continue;'
        if isinstance(node, CallNode):
            if node.name == '\u0686\u0627\u067e': return gen_stmt(PrintNode(node.args[0]), func_name, local_vars, decls)
            if node.name == '\u0646\u0648\u0639': return ''
            if node.name == '\u0646\u0648\u0634\u062a\u0646_\u0641\u0627\u06cc\u0644':
                path = gen_expr(node.args[0], func_name, local_vars, decls)
                content = gen_expr(node.args[1], func_name, local_vars, decls)
                return f'write_file({path}, {content});'
            if node.name == '\u062e\u0648\u0627\u0646\u062f\u0646_\u0641\u0627\u06cc\u0644':
                path = gen_expr(node.args[0], func_name, local_vars, decls)
                return f'read_file({path});'
            if node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0639\u062f\u062f':
                arg = gen_expr(node.args[0], func_name, local_vars, decls)
                return f'atof({arg});'
            if node.name == '\u062a\u0628\u062f\u06cc\u0644_\u0628\u0647_\u0631\u0634\u062a\u0647':
                arg = gen_expr(node.args[0], func_name, local_vars, decls)
                return f'// convert to string: {arg} (no-op)'
            if node.name == '\u0637\u0648\u0644':
                arg = node.args[0]
                if isinstance(arg, VarNode) and is_dict_var(arg.name, func_name):
                    return f'printf("%d\\n", dict_length({c_name(arg.name, func_name)}));'
            if node.name == '\u062e\u0637\u0627_\u0628\u062f\u0647':
                msg = gen_expr(node.args[0], func_name, local_vars, decls)
                return f'strcpy(__try_error, {msg}); longjmp(__try_buf, 1);'
            # method call
            if '.' in node.name:
                parts = node.name.split('.')
                obj_name = parts[0]; method = parts[1]
                obj_var = c_name(obj_name, func_name)
                cls_name = var_info[obj_name]['class_name']
                safe_fn = f'{cls_name}_{method}'
                if node.args:
                    args = ', '.join(gen_expr(a, func_name, local_vars, decls) for a in node.args)
                    return f'{safe_fn}({obj_var}, {args});'
                else:
                    return f'{safe_fn}({obj_var});'
            args = ', '.join(gen_expr(a, func_name, local_vars, decls) for a in node.args)
            return f'{node.name}({args});'
        if isinstance(node, ReturnNode):
            e = gen_expr(node.expr, func_name, local_vars, decls)
            return f'return {e};'
        if isinstance(node, ImportNode):
            with open(node.filepath, 'r', encoding='utf-8') as f:
                imported_code = f.read()
            imported_lexer = Lexer(imported_code)
            imported_parser = Parser(imported_lexer.tokens)
            imported_ast = imported_parser.parse()
            imported_statements = []
            for s in imported_ast:
                if not isinstance(s, FunctionNode) and not isinstance(s, ClassNode):
                    imported_statements.append(s)
            imported_body = gen_block(imported_statements, func_name, local_vars, decls)
            return f'// imported from {node.filepath}\n{imported_body}'
        if isinstance(node, TryNode):
            try_body = gen_block(node.try_body if isinstance(node.try_body, list) else [node.try_body], func_name, local_vars, decls)
            catch_decls = []
            catch_body = gen_block(node.catch_body if isinstance(node.catch_body, list) else [node.catch_body], func_name, local_vars, catch_decls)
            catch_var = node.catch_var
            catch_part = f'        strcpy({c_name(catch_var, func_name)}, __try_error);\n'
            if catch_decls:
                catch_part += '\n'.join('        ' + d for d in catch_decls) + '\n'
            catch_part += catch_body
            return (
                f'{{\n'
                f'    void (*old_handler)(int) = signal(SIGFPE, __try_signal_handler);\n'
                f'    if (setjmp(__try_buf) == 0) {{\n'
                f'{try_body}\n'
                f'    }} else {{\n'
                f'        signal(SIGFPE, old_handler);\n'
                f'{catch_part}\n'
                f'    }}\n'
                f'    signal(SIGFPE, old_handler);\n'
                f'}}'
            )
        if isinstance(node, ThrowNode):
            msg = gen_expr(node.message_expr, func_name, local_vars, decls)
            return f'strcpy(__try_error, {msg}); longjmp(__try_buf, 1);'
        if isinstance(node, ClassNode):
            return f'// class {node.name}'
        if isinstance(node, DotNode):
            return '0;'
        return ''

    def gen_block(stmts, func_name, local_vars, decls):
        lines = []
        for s in stmts:
            line = gen_stmt(s, func_name, local_vars, decls)
            if line: lines.append(line)
        return '\n'.join(lines)

    def gen_func_body(body_stmts, func_name=None):
        decls = []
        local_vars = set()
        if func_name and func_name in functions:
            f = functions[func_name]
            if isinstance(f, Function):
                local_vars = set(f.params)
        body = gen_block(body_stmts, func_name, local_vars, decls)
        out = ''
        if decls: out += '\n'.join('    '+d for d in decls) + '\n'
        out += body
        return out

    # Emit function definitions and collect prototypes
    func_code = ''
    for fn, fnode in functions.items():
        if not isinstance(fnode, Function):
            continue
        if fn in classes:
            continue
        # determine params and return type
        if '_' in fn and fn.split('_')[0] in classes:
            cls_name = fn.split('_')[0]
            pdecls = [f'struct_{cls_name}* self']
            for p in fnode.params:
                t = param_types.get((fn, p), 'double')
                pdecls.append(f'{"char*" if t=="string" else "double"} {p}')
        else:
            pdecls = []
            for p in fnode.params:
                t = param_types.get((fn, p), 'double')
                pdecls.append(f'{"char*" if t=="string" else "double"} {p}')
        has_return = any(isinstance(s, ReturnNode) or (isinstance(s,list) and any(isinstance(ss,ReturnNode) for ss in s)) for s in fnode.body)
        ret = 'double' if has_return else 'void'
        # add prototype
        forward_decls.append(f'{ret} {fn}({", ".join(pdecls)});')
        # definition
        func_code += f'{ret} {fn}({", ".join(pdecls)}) {{\n'
        func_code += gen_func_body(fnode.body, func_name=fn)
        func_code += '\n}\n\n'

    main_code = 'int main() {\n'
    main_code += gen_func_body(statements, func_name=None)
    main_code += '\n    return 0;\n}\n'

    # Assemble final code: includes, helpers, prototypes, functions, main
    final_code = c_code
    if forward_decls:
        final_code += '\n// prototypes\n'
        final_code += '\n'.join(forward_decls) + '\n\n'
    final_code += func_code
    final_code += main_code

    with open(output_c_file, 'w', encoding='utf-8') as f:
        f.write(final_code)
    print(f"C code generated: {output_c_file}")

    exe = output_c_file.replace('.c','')
    res = subprocess.run(['gcc', output_c_file, '-o', exe], capture_output=True, text=True)
    if res.returncode!=0:
        print("Compilation errors:"); print(res.stderr)
        return None
    print(f"Executable created: {exe}")
    return exe

if __name__=='__main__':
    if len(sys.argv)<2:
        print("Usage: python compiler.py <input.fs> [output.c]"); sys.exit(1)
    inp = sys.argv[1]
    outc = sys.argv[2] if len(sys.argv)>2 else inp.replace('.fs','.c')
    with open(inp,'r',encoding='utf-8') as f: code = f.read()
    exe = compile_to_c(code, outc)
    if exe:
        print("Running the compiled program:")
        subprocess.run(['./'+exe])
'''

with open('compiler.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('compiler.py written successfully')
