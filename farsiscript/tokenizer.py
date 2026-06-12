import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

def persian_float_to_float(s):
    mapping = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٫': '.'
    }
    converted = ''.join(mapping.get(ch, ch) for ch in s)
    return float(converted)

class Lexer:
    def __init__(self, source):
        self.source = source
        self.line = 1
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        keywords = {
            'تابع': 'FUNC',
            'برگردان': 'RETURN',
            'چاپ': 'PRINT',
            'خواندن': 'READ',
            'اگر': 'IF',
            'درغیراینصورت': 'ELSE',
            'تاوقتی': 'WHILE',
            'برای': 'FOR',
            'در': 'IN',
            'بشکن': 'BREAK',
            'ادامه': 'CONTINUE',
            'استفاده': 'IMPORT',
            'سعی': 'TRY',
            'بگیر': 'CATCH',
            'خطا_بده': 'THROW',
            'کلاس': 'CLASS',         # new
            'این': 'THIS',           # new
        }
        token_specs = [
            ('COMMENT',   r'//[^\n]*'),
            ('REAL',      r'[0-9۰-۹]+\.[0-9۰-۹]+'),
            ('NUMBER',    r'\d+(\.\d*)?'),
            ('STRING',    r'"[^"]*"'),
            ('IDENT',     r'[آ-یa-zA-Z_][آ-یa-zA-Z0-9_]*'),
            ('EQ',        r'=='),
            ('NEQ',       r'!='),
            ('ASSIGN',    r'='),
            ('DOT',       r'\.'),           # needed for این.نام
            ('PLUS',      r'\+'),
            ('MINUS',     r'-'),
            ('MUL',       r'\*'),
            ('DIV',       r'/'),
            ('LPAREN',    r'\('),
            ('RPAREN',    r'\)'),
            ('LBRACE',    r'\{'),
            ('RBRACE',    r'\}'),
            ('LBRACKET',  r'\['),
            ('RBRACKET',  r'\]'),
            ('COLON',     r':'),
            ('COMMA',     r','),
            ('SEMI',      r';'),
            ('GT',        r'>'),
            ('LT',        r'<'),
            ('SKIP',      r'[ \t\u200c\u200d\u200e\u200f\u202a-\u202e]+'),
            ('NEWLINE',   r'\n'),
            ('MISMATCH',  r'.'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)
        line_start = 0
        for mo in re.finditer(tok_regex, self.source, re.UNICODE):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start + 1
            if kind == 'NEWLINE':
                self.line += 1
                line_start = mo.end()
                continue
            elif kind == 'SKIP':
                continue
            elif kind == 'COMMENT':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f"{value} خطای ناشناخته در خط {self.line}")
            elif kind == 'REAL':
                value = persian_float_to_float(value)
            elif kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'IDENT' and value in keywords:
                kind = keywords[value]
            self.tokens.append(Token(kind, value, self.line, column))
        return self.tokens
