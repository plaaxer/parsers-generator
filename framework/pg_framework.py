from framework.context_free_grammar import ContextFreeGrammar
from framework.parser_generator import ParserGenerator
class PgFramework:
    def __init__(self, application):
        self.applicationInterface = application
        self.parsers = {}
        self.current_parser = None

    def generate(self, context_free_grammar_str: str, reserved_words: list, name: str = "Parser"):
        """Endpoint para gerar o parser SLR a partir de uma string de gramática e palavras reservadas."""

        if self.parsers.get(name):
            raise ValueError(f"Parser com o nome '{name}' já existe. Escolha outro nome.")

        grammar = ParserGenerator._parse_grammar_from_string(context_free_grammar_str, reserved_words)

        print("\n--- Gramática Carregada e Estruturada ---")
        print(grammar)

        slr_parser = ParserGenerator.generate_parser(grammar, name)

        print("\n--- Analisador SLR Gerado ---")
        print(slr_parser)

        self.parsers[name] = slr_parser
        self.current_parser = slr_parser

    
    def parse(self, tokens: list, verbose: bool = False):

        if not self.current_parser:
            raise ValueError("Nenhum parser selecionado.")
        
        return self.current_parser.parse(tokens, verbose)

    # métodos de manipulação do front-end

    def get_current_parser(self):
        if not self.current_parser:
            return "Nenhum parser selecionado."
        return self.current_parser.name
    
    def get_parsers(self):
        return list(self.parsers.keys())
    
    def select_parser(self, name: str):
        if name not in self.parsers:
            raise ValueError(f"Parser com o nome '{name}' não encontrado.")
        self.current_parser = self.parsers[name]

