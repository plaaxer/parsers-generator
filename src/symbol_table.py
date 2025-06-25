class SymbolTable:
    def __init__(self, reserved_words):
        """
        Inicializa a tabela de símbolos com palavras reservadas.
        
        Args:
            reserved_words: Lista de tuplas (lexema, token_type) para palavras reservadas
                            Ex: [('if', 'PR'), ('else', 'PR'), ('for', 'PR')]
        """
        self.symbols = []  # Armazenará tuplas (lexema, token_type, line)
        self.line_counter = 1  # Contador de linhas (1-indexed)
        
        # Adiciona palavras reservadas
        for lexeme, token_type in reserved_words:
            self._add_symbol(lexeme, token_type)

    def _add_symbol(self, lexeme, token_type):
        """Adiciona um símbolo à tabela, verificando duplicatas"""
        # Verifica se o lexema já existe
        for entry in self.symbols:
            if entry[0] == lexeme:
                raise ValueError(f"Multiple defined name: '{lexeme}'")
        
        # Adiciona nova entrada
        self.symbols.append((lexeme, token_type, self.line_counter))
        self.line_counter += 1

    def lookup(self, lexeme):
        """
        Busca um lexema na tabela do final para o início.
        Retorna:
            - Para palavras reservadas: <lexema,token_type>
            - Para identificadores: <id,line>
            - None se não encontrado
        """
        # Busca reversa (do final para o início)
        for i in range(len(self.symbols)-1, -1, -1):
            stored_lexeme, token_type, line = self.symbols[i]
            if stored_lexeme == lexeme:
                if token_type != 'ID':
                    return f"<{lexeme},{token_type}>"
                return f"<id,{line}>"
        return None

    def add_identifier(self, lexeme):
        """Adiciona um identificador à tabela e retorna seu token"""
        # Verifica se já existe
        if any(entry[0] == lexeme for entry in self.symbols):
            raise ValueError(f"Identifier already exists: '{lexeme}'")
        
        # Adiciona novo identificador
        self._add_symbol(lexeme, 'ID')
        return f"<id,{self.line_counter - 1}>"  # line_counter foi incrementado em _add_symbol

    def __str__(self):
        """Representação da tabela para debug"""
        return "\n".join(
            f"Line {line}: {lexeme} : {token_type}"
            for lexeme, token_type, line in self.symbols
        )

    def __repr__(self):
        return str(self)
