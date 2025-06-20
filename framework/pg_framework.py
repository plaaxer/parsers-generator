from framework.context_free_grammar import ContextFreeGrammar

class PgFramework:
    def __init__(self, application):
        self.applicationInterface = application
        self.grammar = None # Atributo para armazenar o objeto da gramática

    @staticmethod
    def _parse_from_string(grammar_str: str, reserved_words: list) -> ContextFreeGrammar:
        """
        Método auxiliar estático que processa uma string e retorna um objeto ContextFreeGrammar.
        """
        productions_dict = {}
        non_terminals = set()
        all_symbols = set()
        start_symbol = None

        lines = grammar_str.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            
            # O formato da gramática é especificado como "<Não terminal> ::= <Corpo da produção>" 
            head, body_str = line.split('::=')
            head = head.strip()
            body_symbols = body_str.strip().split()

            non_terminals.add(head)
            if start_symbol is None:
                start_symbol = head
            
            all_symbols.update(body_symbols)
            productions_dict.setdefault(head, []).append(body_symbols)

        terminals = all_symbols - non_terminals
        # A lista de palavras reservadas também compõe os terminais 
        terminals.update(reserved_words)

        return ContextFreeGrammar(
            non_terminals=non_terminals,
            terminals=terminals,
            productions=productions_dict,
            start_symbol=start_symbol
        )

    def generate(self, context_free_grammar_str: str, reserved_words: list):
        """
        Orquestra a criação do analisador. Começa processando a gramática de entrada.
        """
        self.grammar = PgFramework._parse_from_string(context_free_grammar_str, reserved_words)

        print("--- Gramática Carregada e Estruturada ---")
        print(self.grammar)