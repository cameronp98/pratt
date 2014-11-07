from parser import TopDownParser

class LogicParser(TopDownParser):
    def _define_symbols(self):

        self.symbol("(identifier)").nud = lambda self: self
        self.symbol("(dec_literal)").nud = lambda self: self
        self.symbol("(hex_literal)").nud = lambda self: self
        self.symbol("(oct_literal)").nud = lambda self: self
        self.symbol("(bin_literal)").nud = lambda self: self
        self.symbol("(str_literal)").nud = lambda self: self
        self.symbol("(end)").val = "EOL"

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

        # parenthesis
        @self.method(self.symbol("("))
        def nud(self):
            expr = self.parser.expression()
            self.parser.advance(")")
            return expr

        # function call
        @self.method(self.symbol("(", 100))
        def led(self, left):
            if not isinstance(left, self.parser.symbols["(identifier)"]):
                raise SyntaxError("lvalue for call must be identifier")
            self.tag = "call"
            self.arg[0] = left
            self.arg[1] = []
            if self.parser.token.tag != ")":
                self.parser.argument_list(self.arg[1])
            self.parser.advance(")")
            return self

        # assignment
        @self.method(self.symbol("=", 80))
        def led(self, left):
            self.arg[0] = left.val
            self.arg[1] = self.parser.expression()
            return self

        # lambda
        self.symbol(":")

        @self.method(self.symbol("lambda"))
        def nud(self):
            self.arg[0] = []
            if self.parser.token.tag != ":":
                self.parser.argument_list(self.arg[0])
            self.parser.advance(":")
            self.arg[1] = self.parser.expression()
            return self

        # list
        self.symbol(",")
        self.symbol("]")

        @self.method(self.symbol("["))
        def nud(self):
            self.tag = "list"
            self.arg[0] = []
            if self.parser.token.tag != "]":
                self.parser.argument_list(self.arg[0])
            self.parser.advance("]")
            return self

    def evaluate(self, expr):
        ast = self.parse(expr)
        return ast


def main():
    parser = LogicParser()
    while True:
        print(parser.evaluate(input("> ")))

if __name__ == '__main__':
    main()
