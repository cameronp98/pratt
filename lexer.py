from collections import namedtuple
import re

ops = "|".join(map(re.escape, \
    ("+", "-", "*", "/", "^", "?", ":", "and", "or", "not", "=")))

RULES_DEFAULT = [
    (r"\d+(?:\d+)?",        "(dec_literal)"),
    (r"0o[0-7]+",           "(oct_literal)"),
    (r"0x[0-9a-f]+",        "(hex_literal)"),
    (r"0b[01]+",            "(bin_literal)"),
    (r"\"(.+?)\"",          "(str_literal)"),
    (r"[\(\)\[\]\{\}]",     "(parenthesis)"),
    (r"[\;\:\,\.]",         "(separator)"),
    (r"{}".format(ops),     "(operator)"),
    (r"[a-zA-Z_]+",         "(identifier)"),
]

# global scanner
scanner = None

Token = namedtuple("Token", ["tag", "val", "pos"])

class LexerError(BaseException):
    pass


def make_scanner(rules, ignore_whitespace=True):
    handlers = [(reg, make_handler(tag)) for reg,tag in rules]
    if ignore_whitespace:
        handlers.append((r"\s+", None))
    return re.Scanner(handlers)

def make_handler(tag):
    def handler(scanner, val):
        return Token(tag, val, scanner.match.start())
    return handler

class Lexer(object):
    def __init__(self, rules=None):
        self.rules = rules or RULES_DEFAULT
        self.scanner = make_scanner(self.rules)

        self.tokens = None
        self.token = None

    def tokenize(self, text):
        tokens, remainder = self.scanner.scan(text)
        if remainder:
            raise LexerError("Invalid syntax (near '{}')".format(remainder))
        return iter(tokens)