from src.symbol_table import SymbolTable
from src.lexical_framework.gal_framework import AgFramework
from src.parser_framework.pg_framework import PgFramework


class Application:
    def __init__(self):
        self.ag_framework = AgFramework(self)
        self.pg_framework = PgFramework(self)
        self.symbol_table = SymbolTable()
        self.run()

    def run(self):
        pass

    def log(self, message: str):
        print(message)

    def error(self, message: str):
        print(f"ERRO: {message}")

    def warning(self, message: str):
        print(f"AVISO: {message}")
