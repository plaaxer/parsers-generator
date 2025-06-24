class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def add(self, lexeme, token_type):
        self.symbols[lexeme] = token_type

    def lookup(self, lexeme):
        return self.symbols.get(lexeme)

    def exists(self, lexeme):
        return lexeme in self.symbols

    def __str__(self):
        return "\n".join(f"{lexeme} : {token_type}" for lexeme, token_type in self.symbols.items())
