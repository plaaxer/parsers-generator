from src.parser_framework.parser_generator import ParserGenerator
import src.parser_framework.config as config
from typing import List, Tuple
from src.parser_framework.utils import read_file_as_string

class PgFramework:
    def __init__(self, application):
        self.application = application
        self.loaded_parsers = []
        self.current_parser = None

    #     framework.select_parser("Parser")
    #     framework.parse(["id", "+", "id"], verbose=True)
    def generate(self, glc_filename: str, name=config.SYNTAX_ANALYZER_DEFAULT_NAME):
        """Endpoint para gerar o parser SLR a partir de uma gramática e palavras reservadas."""

        for p in self.loaded_parsers:
            if p.name == name:
                raise ValueError(f"Parser com o nome '{name}' já existe. Escolha outro nome.")

        grammar_str = read_file_as_string(glc_filename)
        grammar = ParserGenerator._parse_grammar_from_string(grammar_str)

        print("\n--- Gramática Carregada e Estruturada ---")
        print(grammar)

        slr_parser = ParserGenerator.generate_parser(grammar, name)

        print("\n--- Analisador SLR Gerado ---")
        print(slr_parser)

        self.loaded_parsers.append(slr_parser)
        self.current_parser = slr_parser

        return self.current_parser.name 

    def parse(self, tokens: List[Tuple[str, str]], verbose: bool = False):

        if not self.current_parser:
            raise ValueError("Nenhum parser selecionado.")

        return self.current_parser.parse(tokens, verbose)

    # métodos de manipulação do front-end
    def set_current_parser(self, analyzer_name: str) -> bool:
        for p in self.loaded_parsers:
            if p.name == analyzer_name:
                self.current_parser = p 
                self.application.log(f"Analisador sintático atual definido: {analyzer_name}")
                return True
        self.application.error(f"Analisador sintático '{analyzer_name}' não encontrado.")
        return False

    def get_current_parser(self):
        if not self.current_parser:
            return "Nenhum parser selecionado."
        return self.current_parser.name

    def get_parser_info(self, analyzer_name: str):
        for p in self.loaded_parsers:
            if p.name == analyzer_name:
                return p.get_info()
        self.application.error(f"Analisador sintático '{analyzer_name}' não encontrado.")
        return None

    def get_loaded_parsers(self):
        loaded_str = [la.name for la in self.loaded_parsers]
        return loaded_str if loaded_str else None

    def delete_parser(self, analyzer_name: str) -> bool:
        for la in self.loaded_parsers:
            if la.name == analyzer_name:
                self.loaded_parsers.remove(la)
                if self.current_parser == la:
                    self.current_parser = None
                self.application.log(f"Analisador sintático '{analyzer_name}' removido com sucesso.")
                return True
        self.application.error(f"Analisador sintático '{analyzer_name}' não encontrado.")
        return False
