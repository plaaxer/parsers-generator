class SymbolTable:
    def __init__(self, reserved_words):
        self.symbols = []
        self.reserved = {}
        self.index_counter = 0
        
        # Adiciona palavras reservadas
        for word, token_type in reserved_words:
            self.reserved[word] = token_type
    
    def add_identifier(self, lexeme):
        """Adiciona um identificador à tabela e retorna seu índice"""
        if lexeme not in [entry[0] for entry in self.symbols]:
            self.symbols.append((lexeme, 'ID'))
            self.index_counter += 1
        return self.lookup(lexeme)
    
    def lookup(self, lexeme):
        """Retorna o token no formato especificado"""
        if lexeme in self.reserved:
            return f"<{lexeme},{self.reserved[lexeme]}>"
        else:
            for idx, (st_lexeme, _) in enumerate(self.symbols):
                if st_lexeme == lexeme:
                    return f"<id,{idx + 1}>"  # +1 para começar de 1
            return None
    
    def exists(self, lexeme):
        """Verifica se o lexema existe na tabela (como reservado ou ID)"""
        return lexeme in self.reserved or any(lexeme == st_lexeme for st_lexeme, _ in self.symbols)
    
    def __str__(self):
        reserved_str = "\n".join(f"{word} : {token_type}" for word, token_type in self.reserved.items())
        symbols_str = "\n".join(f"{idx+1}: {lexeme} : {token_type}" 
                              for idx, (lexeme, token_type) in enumerate(self.symbols))
        return "Palavras reservadas:\n" + reserved_str + "\n\nIdentificadores:\n" + symbols_str

# class SymbolTable:
#     def __init__(self):
#         self.symbols = {}
#
#     def add(self, lexeme, token_type):
#         self.symbols[lexeme] = token_type
#
#     def lookup(self, lexeme):
#         return self.symbols.get(lexeme)
#
#     def exists(self, lexeme):
#         return lexeme in self.symbols
#
#     def __str__(self):
#         return "\n".join(f"{lexeme} : {token_type}" for lexeme, token_type in self.symbols.items())
