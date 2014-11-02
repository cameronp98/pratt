from collections import namedtuple
import lexer


class SymbolBase(object):
    def __init__(self, val=None):
        self.val = val
        self.arg = [None, None, None]

    def __repr__(self):
        name = self.val or self.tag
        arg = " ".join(map(str, filter(None, self.arg)))
        if any(a is not None for a in arg):
            return "({} {})".format(name, arg)
        return name

    def nud(self):
        raise SyntaxError("invalid symbol '{}' for prefix".format(self.tag))

    def led(self, left):
        raise SyntaxError("invalid symbol '{}' for infix".format(self.tag))


class TopDownParser(object):
    def __init__(self):
        self.lexer = lexer.Lexer()
        self.tokens = []

        self.symbols = {}
        self.context = {}

        self._define_symbols()

    def _define_symbols(self):
        self.symbol("(end)")
        self.symbol("(identifier)")
        self.symbol("(operator)")
        self.symbol("(parenthesis)")
        self.symbol("(")

    def symbol(self, tag, lbp=0):
        try:
            sym = self.symbols[tag]
        except KeyError:
            attrs = {"tag": tag, "lbp": lbp, "parser": self}
            sym = type(tag, (SymbolBase,), attrs)
            self.symbols[tag] = sym

        # increase lbp for duplicate symbols if necessary
        sym.lbp = max(lbp, sym.lbp)

        return sym

    def method(self, sym):
        def binder(func):
            setattr(sym, func.__name__, func)
        return binder

    def infix(self, tag, lbp=0):
        def led(self, left):
            self.arg[0] = left
            self.arg[1] = self.parser.expression(lbp)
            return self
        self.symbol(tag, lbp).led = led

    def infix_r(self, tag, lbp=0):
        def led(self, left):
            self.arg[0] = left
            self.arg[1] = self.parser.expression(lbp - 1)
            return self
        self.symbol(tag, lbp).led = led

    def prefix(self, tag, lbp=0):
        def nud(self):
            self.arg[0] = self.parser.expression(lbp)
            return self
        self.symbol(tag, lbp).nud = nud

    def expression(self, rbp=0):
        t = self.token
        self.token = self.next()
        left = t.nud()
        while rbp < self.token.lbp:
            t = self.token
            self.token = self.next()
            left = t.led(left)
        return left

    def parse(self, expr):
        self._stream = self._token_stream(expr)
        self.token = self.next()
        return self.expression()

    def _token_stream(self, expr):
        for token in self.lexer.tokenize(expr):
            if token.tag in self.symbols:
                yield self.symbols[token.tag](token.val)
            elif token.val in self.symbols:
                yield self.symbols[token.val]()
            else:
                raise SyntaxError("unrecognized token '{}'".format(token))
        yield self.symbols["(end)"]
        
    def next(self):
        return self._stream.__next__()

    def advance(self, tag=None):
        if tag and self.token.tag != tag:
            raise SyntaxError("expected '{}' but got '{}'" \
                .format(tag, self.token.val or token.tag))
        self.token = self.next()
