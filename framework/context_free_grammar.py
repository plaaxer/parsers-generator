import pprint

class ContextFreeGrammar:
    """
    Representa uma Gramática Livre de Contexto (GLC).
    
    Atributos:
        non_terminals (set): Um conjunto de strings representando os símbolos não terminais.
        terminals (set): Um conjunto de strings representando os símbolos terminais.
        productions (dict): Um dicionário mapeando cada não terminal (str) a uma 
                            lista de suas produções (list[list[str]]).
        start_symbol (str): O símbolo inicial da gramática.
    """
    def __init__(self, non_terminals, terminals, productions, start_symbol):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol

    def __repr__(self):
        """Representação em string do objeto para fácil depuração."""
        return (
            f"Símbolo Inicial: {self.start_symbol}\n"
            f"Não Terminais: {sorted(list(self.non_terminals))}\n"
            f"Terminais: {sorted(list(self.terminals))}\n"
            "Produções:\n"
            f"{pprint.pformat(self.productions)}"
        )