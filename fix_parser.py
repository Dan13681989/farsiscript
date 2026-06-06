code = r'''
class ASTNode: pass

class NumberNode(ASTNode):
    def __init__(self, value): self.value = value

class RealNode(ASTNode):
    def __init__(self, value): self.value = value

class StringNode(ASTNode):
    def __init__(self, value): self.value = value[1:-1]

class BinOpNode(ASTNode):
    def __init__(self, left, op, right): self.left=left; self.op=op; self.right=right

class AssignNode(ASTNode):
    def __init__(self, name, expr): self.name=name; self.expr=expr

class AssignIndexNode(ASTNode):
    def __init__(self, name, index, expr): self.name=name; self.index=index; self.expr=expr

class VarNode(ASTNode):
    def __init__(self, name): self.name=name

class CallNode(ASTNode):
    def __init__(self, name, args): self.name=name; self.args=args

class FunctionNode(ASTNode):
    def __init__(self, name, params, body): self.name=name; self.params=params; self.body=body

class ReturnNode(ASTNode):
    def __init__(self, expr): self.expr=expr

class PrintNode(ASTNode):
    def __init__(self, expr): self.expr=expr

class ReadNode(ASTNode):
    def __init__(self, var_name): self.var_name=var_name

class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition=condition; self.body=body; self.else_body=else_body

class WhileNode(ASTNode):
    def __init__(self, condition, body): self.condition=condition; self.body=body

class ForNode(ASTNode):
    def __init__(self, var_name, start_expr=None, end_expr=None, iter_expr=None, body=None):
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.iter_expr = iter_expr
        self.body = body

class BreakNode(ASTNode): pass
class ContinueNode(ASTNode): pass

class ArrayNode(ASTNode):
    def __init__(self, elements): self.elements=elements

class DictNode(ASTNode):
    def __init__(self, pairs): self.pairs = pairs

class IndexNode(ASTNode):
    def __init__(self, array, index): self.array=array; self.index=index

class ImportNode(ASTNode):
    def __init__(self, filepath): self.filepath = filepath

class TryNode(ASTNode):
    def __init__(self, try_body, catch_var, catch_body):
        self.try_body = try_body
        self.catch_var = catch_var
        self.catch_body = catch_body

class ThrowNode(ASTNode):
    def __init__(self, message_expr): self.message_expr = message_expr

class ClassNode(ASTNode):
    def __init__(self, name, body): self.name=name; self.body=body

class ThisNode(ASTNode):
    pass

class DotNode(ASTNode):
    def __init__(self, obj, attr): self.obj=obj; self.attr=attr

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        token = self.current_token()
        if token and token.type == token_type:
            self.pos += 1
            return token
        else:
            expected = token_type
            got = token.type if token else 'EOF'
            raise SyntaxError(f"خطای نحوی در خط {token.line if token else '?'}: انتظار {expected}، دریافت {got}")

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.current_token()
        if token.type == 'FUNC':
            return self.parse_func_def()
        elif token.type == 'RETURN':
            self.eat('RETURN'); expr = self.parse_expression(); self.eat('SEMI'); return ReturnNode(expr)
        elif token.type == 'PRINT':
            self.eat('PRINT'); expr = self.parse_expression(); self.eat('SEMI'); return PrintNode(expr)
        elif token.type == 'READ':
            self.eat('READ'); var_name = self.eat('IDENT').value; self.eat('SEMI'); return ReadNode(var_name)
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'FOR':
            return self.parse_for()
        elif token.type == 'BREAK':
            self.eat('BREAK'); self.eat('SEMI'); return BreakNode()
        elif token.type == 'CONTINUE':
            self.eat('CONTINUE'); self.eat('SEMI'); return ContinueNode()
        elif token.type == 'IMPORT':
            return self.parse_import()
        elif token.type == 'TRY':
            return self.parse_try()
        elif token.type == 'THROW':
            return self.parse_throw()
        elif token.type == 'CLASS':
            return self.parse_class_def()
        elif token.type == 'IDENT':
            name = token.value
            self.eat('IDENT')
            if self.current_token() and self.current_token().type == 'LBRACKET':
                self.eat('LBRACKET'); index = self.parse_expression(); self.eat('RBRACKET')
                if self.current_token() and self.current_token().type == 'ASSIGN':
                    self.eat('ASSIGN'); value = self.parse_expression(); self.eat('SEMI')
                    return AssignIndexNode(name, index, value)
                else:
                    self.eat('SEMI'); return IndexNode(VarNode(name), index)
            elif self.current_token() and self.current_token().type == 'DOT':
                self.eat('DOT'); attr = self.eat('IDENT').value
                node = DotNode(VarNode(name), attr)
                if self.current_token() and self.current_token().type == 'ASSIGN':
                    self.eat('ASSIGN'); expr = self.parse_expression(); self.eat('SEMI')
                    return AssignNode(f'{name}.{attr}', expr)
                elif self.current_token() and self.current_token().type == 'LPAREN':
                    args = self.parse_args(); self.eat('SEMI')
                    return CallNode(f'{name}.{attr}', args)
                else:
                    self.eat('SEMI'); return node
            elif self.current_token() and self.current_token().type == 'ASSIGN':
                self.eat('ASSIGN'); expr = self.parse_expression(); self.eat('SEMI'); return AssignNode(name, expr)
            elif self.current_token() and self.current_token().type == 'LPAREN':
                args = self.parse_args(); self.eat('SEMI'); return CallNode(name, args)
            else:
                self.eat('SEMI'); return VarNode(name)
        elif token.type == 'THIS':
            self.eat('THIS')
            if self.current_token() and self.current_token().type == 'DOT':
                self.eat('DOT')
                attr = self.eat('IDENT').value
                node = DotNode(ThisNode(), attr)
                if self.current_token() and self.current_token().type == 'ASSIGN':
                    self.eat('ASSIGN'); expr = self.parse_expression(); self.eat('SEMI')
                    return AssignNode(f'this.{attr}', expr)
                elif self.current_token() and self.current_token().type == 'LPAREN':
                    args = self.parse_args(); self.eat('SEMI'); return CallNode(f'this.{attr}', args)
                else:
                    self.eat('SEMI'); return node
            else:
                self.eat('SEMI'); return ThisNode()
        elif token.type == 'LBRACE':
            self.eat('LBRACE'); body = []
            while self.current_token() and self.current_token().type != 'RBRACE':
                body.append(self.parse_statement())
            self.eat('RBRACE'); return body
        else:
            raise SyntaxError(f"عبارت نامعتبر در خط {token.line}")

    def parse_class_def(self):
        self.eat('CLASS')
        name = self.eat('IDENT').value
        self.eat('LBRACE')
        body = []
        while self.current_token() and self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.eat('RBRACE')
        return ClassNode(name, body)

    def parse_throw(self):
        self.eat('THROW')
        self.eat('LPAREN')
        message = self.parse_expression()
        self.eat('RPAREN')
        self.eat('SEMI')
        return ThrowNode(message)

    def parse_try(self):
        self.eat('TRY')
        if self.current_token() and self.current_token().value == '\u06a9\u0646':
            self.eat('IDENT')
        try_body = self.parse_statement()
        self.eat('CATCH')
        catch_var = None
        if self.current_token() and self.current_token().type == 'LPAREN':
            self.eat('LPAREN')
            catch_var = self.eat('IDENT').value
            self.eat('RPAREN')
        catch_body = self.parse_statement()
        return TryNode(try_body, catch_var, catch_body)

    def parse_if(self):
        self.eat('IF'); self.eat('LPAREN'); cond = self.parse_expression(); self.eat('RPAREN')
        body = self.parse_statement(); else_body = None
        if self.current_token() and self.current_token().type == 'ELSE':
            self.eat('ELSE')
            if self.current_token() and self.current_token().type == 'IF':
                else_body = self.parse_if()
            else:
                else_body = self.parse_statement()
        return IfNode(cond, body, else_body)

    def parse_while(self):
        self.eat('WHILE'); self.eat('LPAREN'); cond = self.parse_expression(); self.eat('RPAREN')
        body = self.parse_statement(); return WhileNode(cond, body)

    def parse_for(self):
        self.eat('FOR')
        var_name = self.eat('IDENT').value
        if self.current_token() and self.current_token().type == 'IN':
            self.eat('IN')
            iter_expr = self.parse_expression()
            body = self.parse_statement()
            return ForNode(var_name, iter_expr=iter_expr, body=body)
        else:
            if self.current_token() and self.current_token().value == '\u0627\u0632':
                self.eat('IDENT')
                start = self.parse_expression()
                if self.current_token() and self.current_token().value == '\u062a\u0627':
                    self.eat('IDENT')
                    end = self.parse_expression()
                else:
                    raise SyntaxError(f"انتظار 'تا' در خط {self.current_token().line}")
            else:
                raise SyntaxError("حلقه برای فقط با 'از ... تا' یا 'در' پشتیبانی می‌شود")
            body = self.parse_statement()
            return ForNode(var_name, start_expr=start, end_expr=end, body=body)

    def parse_import(self):
        self.eat('IMPORT')
        if self.current_token() and self.current_token().value == '\u0627\u0632':
            self.eat('IDENT')
        filepath = self.eat('STRING').value[1:-1]
        self.eat('SEMI')
        return ImportNode(filepath)

    def parse_func_def(self):
        self.eat('FUNC'); name = self.eat('IDENT').value; self.eat('LPAREN')
        params = []
        if self.current_token() and self.current_token().type != 'RPAREN':
            params.append(self.eat('IDENT').value)
            while self.current_token() and self.current_token().type == 'COMMA':
                self.eat('COMMA'); params.append(self.eat('IDENT').value)
        self.eat('RPAREN'); self.eat('LBRACE')
        body = []
        while self.current_token() and self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.eat('RBRACE'); return FunctionNode(name, params, body)

    def parse_args(self):
        self.eat('LPAREN'); args = []
        if self.current_token() and self.current_token().type != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token() and self.current_token().type == 'COMMA':
                self.eat('COMMA'); args.append(self.parse_expression())
        self.eat('RPAREN'); return args

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        node = self.parse_addition()
        while self.current_token() and self.current_token().type in ('GT', 'LT', 'EQ', 'NEQ'):
            op = self.current_token().type; self.eat(op)
            right = self.parse_addition(); node = BinOpNode(node, op, right)
        return node

    def parse_addition(self):
        node = self.parse_multiplication()
        while self.current_token() and self.current_token().type in ('PLUS', 'MINUS'):
            op = self.current_token().type; self.eat(op)
            right = self.parse_multiplication(); node = BinOpNode(node, op, right)
        return node

    def parse_multiplication(self):
        node = self.parse_primary()
        while self.current_token() and self.current_token().type in ('MUL', 'DIV'):
            op = self.current_token().type; self.eat(op)
            right = self.parse_primary(); node = BinOpNode(node, op, right)
        return node

    def parse_primary(self):
        token = self.current_token()
        if token.type == 'REAL':
            self.eat('REAL'); return RealNode(token.value)
        elif token.type == 'NUMBER':
            self.eat('NUMBER'); return NumberNode(token.value)
        elif token.type == 'STRING':
            self.eat('STRING'); return StringNode(token.value)
        elif token.type == 'IDENT':
            name = token.value; self.eat('IDENT')
            if self.current_token() and self.current_token().type == 'LPAREN':
                args = self.parse_args(); node = CallNode(name, args)
            else:
                node = VarNode(name)
            while self.current_token() and self.current_token().type == 'LBRACKET':
                self.eat('LBRACKET'); index = self.parse_expression(); self.eat('RBRACKET')
                node = IndexNode(node, index)
            if self.current_token() and self.current_token().type == 'DOT':
                self.eat('DOT'); attr = self.eat('IDENT').value
                node = DotNode(node, attr)
                if self.current_token() and self.current_token().type == 'LPAREN':
                    args = self.parse_args()
                    node = CallNode(f'{name}.{attr}', args)   # method call
            return node
        elif token.type == 'THIS':
            self.eat('THIS')
            if self.current_token() and self.current_token().type == 'DOT':
                self.eat('DOT'); attr = self.eat('IDENT').value
                node = DotNode(ThisNode(), attr)
                if self.current_token() and self.current_token().type == 'LPAREN':
                    args = self.parse_args(); return CallNode(f'this.{attr}', args)
                return node
            else:
                return ThisNode()
        elif token.type == 'LBRACKET':
            self.eat('LBRACKET'); elements = []
            if self.current_token() and self.current_token().type != 'RBRACKET':
                elements.append(self.parse_expression())
                while self.current_token() and self.current_token().type == 'COMMA':
                    self.eat('COMMA'); elements.append(self.parse_expression())
            self.eat('RBRACKET'); node = ArrayNode(elements)
            while self.current_token() and self.current_token().type == 'LBRACKET':
                self.eat('LBRACKET'); index = self.parse_expression(); self.eat('RBRACKET')
                node = IndexNode(node, index)
            return node
        elif token.type == 'LBRACE':
            return self.parse_dict()
        elif token.type == 'LPAREN':
            self.eat('LPAREN'); node = self.parse_expression(); self.eat('RPAREN'); return node
        else:
            raise SyntaxError(f"عبارت اولیه نامعتبر در خط {token.line}")

    def parse_dict(self):
        self.eat('LBRACE')
        pairs = []
        if self.current_token() and self.current_token().type != 'RBRACE':
            key = self.parse_expression()
            self.eat('COLON')
            value = self.parse_expression()
            pairs.append((key, value))
            while self.current_token() and self.current_token().type == 'COMMA':
                self.eat('COMMA')
                key = self.parse_expression()
                self.eat('COLON')
                value = self.parse_expression()
                pairs.append((key, value))
        self.eat('RBRACE')
        return DictNode(pairs)
'''

with open('parser.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('parser.py written successfully')
