from src.lexical_framework.gal_framework import GalFramework
from src.parser_framework.pg_framework import PgFramework


class Application:
    def __init__(self):
        self.framework = GalFramework(self)
        self.pg_framework = PgFramework(self)
        self.run()

    def run(self):
        pass

    def log(self, message: str):
        print(message)

    def error(self, message: str):
        print(f"ERRO: {message}")

    def warning(self, message: str):
        print(f"AVISO: {message}")
