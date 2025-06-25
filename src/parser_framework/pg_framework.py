from src.parser_framework.parser_generator import ParserGenerator


class PgFramework:
    def __init__(self, application):
        self.application = application
        self.loaded_parsers = []
        self.current_parser = None
        self.parsers = {}

    def generate(self, context_free_grammar_str: str, reserved_words: list, name: str = "Parser"):
        """Endpoint para gerar o parser SLR a partir de uma string de gramática e palavras reservadas."""

        if self.parsers.get(name):
            raise ValueError(
                f"Parser com o nome '{name}' já existe. Escolha outro nome.")

        grammar = ParserGenerator._parse_grammar_from_string(
            context_free_grammar_str, reserved_words)

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
                if self.current_lexical_analyzer == la:
                    self.current_lexical_analyzer = None
                self.application.log(f"Analisador sintático '{analyzer_name}' removido com sucesso.")
                return True
        self.application.error(f"Analisador sintático '{analyzer_name}' não encontrado.")
        return False


    def select_parser(self, name: str):
        if name not in self.parsers:
            raise ValueError(f"Parser com o nome '{name}' não encontrado.")
        self.current_parser = self.parsers[name]
