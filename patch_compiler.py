# This script adds a few lines to compiler.py so it ignores class-related constructs

with open('compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to find the gen_stmt function and add a special case before the line:
#     if isinstance(node, AssignNode):
# We'll also add a special case for CallNode that contains a dot.

# Strategy:
# 1. In gen_stmt, before "if isinstance(node, AssignNode):", add:
#    if isinstance(node, AssignNode) and isinstance(node.expr, CallNode):
#        fn = node.expr.name
#        if '.' in fn or functions.get(fn) is not None and not isinstance(functions.get(fn), Function):
#            return 'var_{} = 0; /* class instance */'.format(c_name(node.name, func_name))
# 2. In gen_stmt, before "if isinstance(node, CallNode):", add a check for dot calls:
#    if isinstance(node, CallNode) and '.' in node.name:
#        return '/* method call {} ignored */'.format(node.name)

# We'll search for lines that match these patterns and insert before them.
# Also we need to make sure the `functions` variable is accessible inside gen_stmt (it is a closure variable, so fine).

output = []
in_gen_stmt = False
indent = ''
for i, line in enumerate(lines):
    output.append(line)
    # Detect entering gen_stmt function
    if 'def gen_stmt(node, func_name, local_vars, decls):' in line:
        in_gen_stmt = True
        # get indentation
        indent = line[:len(line) - len(line.lstrip())]
    if in_gen_stmt and 'if isinstance(node, AssignNode):' in line and 'AssignNode' in line:
        # Insert before this line
        output.insert(len(output)-1, 
            indent + '    if isinstance(node, AssignNode) and isinstance(node.expr, CallNode):\n' +
            indent + '        fn = node.expr.name\n' +
            indent + '        if \'.\' in fn or (fn in functions and not isinstance(functions[fn], Function)):\n' +
            indent + '            return f\'{c_name(node.name, func_name)} = 0; /* class instance */\'\n'
        )
    if in_gen_stmt and 'if isinstance(node, CallNode):' in line:
        # Insert before this line
        output.insert(len(output)-1,
            indent + '    if isinstance(node, CallNode) and \'.\' in node.name:\n' +
            indent + '        return \'/* method call {} ignored */\'\n'
        )
    if in_gen_stmt and 'def gen_block(' in line:
        in_gen_stmt = False

with open('compiler.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print('compiler.py patched successfully')
