from src.parser_framework.context_free_grammar import ContextFreeGrammar
from src.parser_framework.slr_parser import SLRParser
import src.parser_framework.config as config 

class ParserGenerator:
    
    @staticmethod
    def _parse_grammar_from_string(grammar_str: str, reserved_words: list) -> ContextFreeGrammar:
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
            
            # "<Não terminal> ::= <Corpo da produção>" 
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

    @staticmethod
    def generate_parser(grammar: ContextFreeGrammar, name: str):
        """
        Gera um objeto de parser SLR completo a partir da gramática fornecida.
        """
        # 1. Aumentar a gramática
        augmented_grammar, new_start_symbol = ParserGenerator._augment_grammar(grammar)
        productions_list = [(head, body) for head, bodies in augmented_grammar.productions.items() for body in bodies]

        # 2. Calcular conjuntos First e Follow
        first_sets = ParserGenerator._compute_first_sets(augmented_grammar)
        follow_sets = ParserGenerator._compute_follow_sets(augmented_grammar, first_sets)

        # 3. Calcular coleção canônica de itens LR(0)
        canonical_collection, goto_map = ParserGenerator._build_canonical_collection(augmented_grammar)

        # 4. Construir a tabela de parsing SLR (como um dicionário intermediário)
        action_table = {}
        goto_table = {}
        for i, item_set in enumerate(canonical_collection):
            action_table[i] = {}
            goto_table[i] = {}
            for symbol in augmented_grammar.non_terminals:
                if (i, symbol) in goto_map:
                    goto_table[i][symbol] = goto_map[(i, symbol)]
            for item in item_set:
                head, body, dot_pos = item
                if dot_pos < len(body):
                    next_symbol = body[dot_pos]
                    if next_symbol in augmented_grammar.terminals and (i, next_symbol) in goto_map:
                        target_state = goto_map[(i, next_symbol)]
                        if next_symbol in action_table[i] and action_table[i][next_symbol][0] == 'reduce':
                            raise ValueError(f"Conflito Shift/Reduce no estado {i} para o símbolo '{next_symbol}'")
                        action_table[i][next_symbol] = ('shift', target_state)
                else:
                    if head == new_start_symbol:
                        action_table[i][config.END_OF_INPUT] = ('accept',)
                    else:
                        prod_to_reduce = (head, body)
                        prod_index = productions_list.index(prod_to_reduce)
                        for terminal in follow_sets[head]:
                            if terminal in action_table[i]:
                                raise ValueError(f"Conflito no estado {i} para o símbolo '{terminal}'")
                            action_table[i][terminal] = ('reduce', prod_index)
        
        parsing_table_dict = {'action': action_table, 'goto': goto_table, 'productions': productions_list}
        
        # 5. Criar e retornar a instância do parser
        return SLRParser(parsing_table_dict, name)

    @staticmethod
    def _augment_grammar(grammar: ContextFreeGrammar):
        new_start_symbol = grammar.start_symbol + "'"
        while new_start_symbol in grammar.non_terminals:
             new_start_symbol += "'"
        
        augmented_prods = {new_start_symbol: [(grammar.start_symbol,)]}
        # Deep copy das produções originais
        for head, bodies in grammar.productions.items():
            augmented_prods[head] = [tuple(body) for body in bodies]

        return ContextFreeGrammar(
            non_terminals=grammar.non_terminals.union({new_start_symbol}),
            terminals=grammar.terminals,
            productions=augmented_prods,
            start_symbol=new_start_symbol
        ), new_start_symbol

    @staticmethod
    def _compute_first_sets(grammar: ContextFreeGrammar):
        first = {nt: set() for nt in grammar.non_terminals}
        changed = True
        while changed:
            changed = False
            for head, bodies in grammar.productions.items():
                for body in bodies:
                    # Regra para produções com épsilon
                    if body == (config.EPSILON,):
                        if config.EPSILON not in first[head]:
                            first[head].add(config.EPSILON)
                            changed = True
                        continue
                    
                    # Iterar sobre os símbolos da produção
                    for symbol in body:
                        # Se for um terminal, adicione-o ao conjunto First
                        if symbol in grammar.terminals:
                            if symbol not in first[head]:
                                first[head].add(symbol)
                                changed = True
                            break # Para a próxima produção
                        
                        # Se for um não-terminal
                        if symbol in grammar.non_terminals:
                            first_of_symbol = first[symbol]
                            # Adicionar tudo de First(symbol) exceto épsilon
                            for f in first_of_symbol - {config.EPSILON}:
                                if f not in first[head]:
                                    first[head].add(f)
                                    changed = True
                            
                            # Se épsilon não está em First(symbol), parar
                            if config.EPSILON not in first_of_symbol:
                                break
                    else: # Loop completou sem break (todos os símbolos derivam épsilon)
                        if config.EPSILON not in first[head]:
                            first[head].add(config.EPSILON)
                            changed = True
        return first

    @staticmethod
    def _get_first_of_sequence(sequence, first_sets, terminals):
        """Calcula o conjunto First para uma sequência de símbolos."""
        result = set()
        for symbol in sequence:
            if symbol in terminals:
                result.add(symbol)
                return result
            
            symbol_first = first_sets.get(symbol, set())
            result.update(symbol_first - {config.EPSILON})
            if config.EPSILON not in symbol_first:
                return result
        
        result.add(config.EPSILON)
        return result

    @staticmethod
    def _compute_follow_sets(grammar: ContextFreeGrammar, first_sets):
        follow = {nt: set() for nt in grammar.non_terminals}
        follow[grammar.start_symbol].add(config.END_OF_INPUT)
        
        changed = True
        while changed:
            changed = False
            for head, bodies in grammar.productions.items():
                for body in bodies:
                    for i, symbol in enumerate(body):
                        if symbol in grammar.non_terminals:
                            beta = body[i+1:]
                            
                            # Regra 2: A -> αBβ
                            if beta:
                                first_of_beta = ParserGenerator._get_first_of_sequence(
                                    beta, first_sets, grammar.terminals
                                )
                                # Adicionar First(β) \ {ε} a Follow(B)
                                for f in first_of_beta - {config.EPSILON}:
                                    if f not in follow[symbol]:
                                        follow[symbol].add(f)
                                        changed = True
                                
                                # Se ε ∈ First(β), adicionar Follow(A) a Follow(B)
                                if config.EPSILON in first_of_beta:
                                    for f in follow[head]:
                                        if f not in follow[symbol]:
                                            follow[symbol].add(f)
                                            changed = True
                            
                            # Regra 3: A -> αB
                            else:
                                for f in follow[head]:
                                    if f not in follow[symbol]:
                                        follow[symbol].add(f)
                                        changed = True
        return follow

    @staticmethod
    def _closure(items, grammar: ContextFreeGrammar):
        """Calcula o fecho de um conjunto de itens LR(0)."""
        closure_set = set(items)
        worklist = list(items)
        
        while worklist:
            item = worklist.pop(0)
            head, body, dot_pos = item
            
            if dot_pos < len(body):
                next_symbol = body[dot_pos]
                if next_symbol in grammar.non_terminals:
                    for prod_body in grammar.productions.get(next_symbol, []):
                        new_item = (next_symbol, prod_body, 0)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            worklist.append(new_item)
        return frozenset(closure_set)

    @staticmethod
    def _goto(item_set, symbol, grammar: ContextFreeGrammar):
        """Calcula a função GOTO."""
        new_items = set()
        for item in item_set:
            head, body, dot_pos = item
            if dot_pos < len(body) and body[dot_pos] == symbol:
                new_items.add((head, body, dot_pos + 1))
        return ParserGenerator._closure(new_items, grammar)

    @staticmethod
    def _build_canonical_collection(grammar: ContextFreeGrammar):
        """Constrói a coleção canônica de conjuntos de itens LR(0)."""
        all_symbols = grammar.non_terminals.union(grammar.terminals)
        
        # O item inicial é (S' -> .S, 0)
        initial_prod_body = grammar.productions[grammar.start_symbol][0]
        initial_item = (grammar.start_symbol, initial_prod_body, 0)
        
        # I0 = CLOSURE({[S' -> .S]})
        i0 = ParserGenerator._closure({initial_item}, grammar)
        
        states = [i0]
        state_map = {i0: 0}
        goto_map = {}
        
        worklist = [0] # Fila de trabalho com índices de estados
        
        while worklist:
            state_idx = worklist.pop(0)
            current_state_items = states[state_idx]
            
            for symbol in all_symbols:
                next_state_items = ParserGenerator._goto(current_state_items, symbol, grammar)
                
                if not next_state_items:
                    continue
                
                if next_state_items not in state_map:
                    # Novo estado encontrado
                    new_state_idx = len(states)
                    states.append(next_state_items)
                    state_map[next_state_items] = new_state_idx
                    worklist.append(new_state_idx)
                    goto_map[(state_idx, symbol)] = new_state_idx
                else:
                    # Estado já existe
                    goto_map[(state_idx, symbol)] = state_map[next_state_items]
                    
        return states, goto_map
