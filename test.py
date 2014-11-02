from parser import TopDownParser

class LogicParser(TopDownParser):
    def _define_symbols(self):

        self.symbol("(identifier)").nud = lambda self: self
        self.symbol("(dec_literal)").nud = lambda self: self
        self.symbol("(hex_literal)").nud = lambda self: self
        self.symbol("(oct_literal)").nud = lambda self: self
        self.symbol("(bin_literal)").nud = lambda self: self
        self.symbol("(end)")

        self.infix("+", 10)
        self.infix("-", 10)

        self.infix("or", 10)

        self.infix("*", 20)
        self.infix("/", 20)

        self.infix("and", 20)

        self.prefix("not", 30)
        self.prefix("-", 30)

        self.infix_r("^", 50)

        self.symbol(")")

        @self.method(self.symbol("("))
        def nud(self):
            expr = self.parser.expression()
            self.parser.advance(")")
            return expr

        @self.method(self.symbol("=", 80))
        def led(self, left):
            self.arg[0] = left.val
            self.arg[1] = self.parser.expression()
            return self


def main():
    parser = LogicParser()
    ast = parser.parse("area = pi * r ^ 2")
    print(ast)

if __name__ == '__main__':
    main()
