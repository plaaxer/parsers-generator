import pprint

class ContextFreeGrammar:

    def __init__(self, non_terminals, terminals, productions, start_symbol):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol

    def __repr__(self):
        return (
            f"Símbolo Inicial: {self.start_symbol}\n"
            f"Não Terminais: {sorted(list(self.non_terminals))}\n"
            f"Terminais: {sorted(list(self.terminals))}\n"
            "Produções:\n"
            f"{pprint.pformat(self.productions)}"
        )