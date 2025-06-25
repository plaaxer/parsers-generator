from src.symbol_table import SymbolTable
from src.scanner_framework.sg_framework import SgFramework
from src.parser_framework.pg_framework import PgFramework


class Application:
    def __init__(self):
        self.sg_framework = SgFramework(self)
        self.pg_framework = PgFramework(self)
        self.symbol_table = SymbolTable([])
        self.run()

    def analyze(self, input_str):
        tokens = self.sg_framework.analyze(input_str)
        print("Symbol table", self.symbol_table)
        # self.pg_framework.parse(tokens, verbose=True)
        pass

    def run(self):
        pass

    def log(self, message: str):
        print(message)

    def error(self, message: str):
        print(f"ERRO: {message}")

    def warning(self, message: str):
        print(f"AVISO: {message}")
