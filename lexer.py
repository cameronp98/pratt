from collections import namedtuple
import re

def any(*args):
    return "|".join(map(re.escape, args))

ops = any("+", "-", "*", "/", "^", "?", ":", "and", "or", "not", "=")

kwd = any("lambda", "if", "else")

RULES_DEFAULT = [
    (kwd,                   "(keyword)"),
    (ops,                   "(operator)"),
    (r"0o[0-7]+",           "(oct_literal)"),
    (r"0x[0-9a-f]+",        "(hex_literal)"),
    (r"0b[01]+",            "(bin_literal)"),
    (r"\d+(?:\.\d+)?",      "(dec_literal)"),
    (r"\"(.+?)\"",          "(str_literal)"),
    (r"[\(\)\[\]\{\}]",     "(parenthesis)"),
    (r"[\;\:\,\.]",         "(separator)"),
    (r"[a-zA-Z_]+",         "(identifier)"),
]

Token = namedtuple("Token", ["tag", "val", "pos"])

class LexerError(BaseException):
    pass


def make_scanner(rules, ignore_whitespace=True):
    """
    Turns a list of (regex, token_name) tuples into callbacks re.Scanner
    """
    handlers = [(reg, make_handler(tag)) for reg,tag in rules]
    if ignore_whitespace:
        handlers.append((r"\s+", None))
    return re.Scanner(handlers)

def make_handler(tag):
    def handler(scanner, val):
        return Token(tag, val, scanner.match.start())
    return handler

class Lexer(object):
    """
    Wrapper for re.Scanner; takes token rules as list of (regex, name) tuples
      e.g. [("\d+", "NUMBER"), ...]
    """
    def __init__(self, rules=None):
        if rules is None:
            rules = RULES_DEFAULT
        self.scanner = make_scanner(rules)

    def tokenize(self, text):
        tokens, remainder = self.scanner.scan(text)
        if remainder:
            raise LexerError("Invalid syntax (near '{}')".format(remainder))
        return iter(tokens)
