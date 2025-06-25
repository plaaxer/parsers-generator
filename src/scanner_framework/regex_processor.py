from src.scanner_framework.automatas.deterministic_automata import DeterministicFiniteAutomata
from typing import Set, Dict, Tuple, List, Optional, FrozenSet


class SyntaxTreeNode:
    _position_counter = 1 # For assigning unique positions to symbol leaves

    def __init__(self, node_type: str, value: Optional[str] = None, children: Optional[List['SyntaxTreeNode']] = None):
        self.node_type: str = node_type  # e.g., 'LITERAL', 'CONCAT', 'UNION', 'STAR', 'PLUS', 'OPTION', 'ENDMARKER'
        self.value: Optional[str] = value # LITERAL/ENDMARKER
        self.children: List[SyntaxTreeNode] = children if children is not None else []

        self.nullable: bool = False
        self.firstpos: Set[int] = set()
        self.lastpos: Set[int] = set()
        
        self.position: Optional[int] = None
        if self.node_type == 'LITERAL' or self.node_type == 'ENDMARKER':
            self.position = SyntaxTreeNode._position_counter
            SyntaxTreeNode._position_counter += 1

    def __repr__(self) -> str:
        return f"Node({self.node_type}, {self.value or ''}, pos:{self.position}, child_count:{len(self.children)})"

class RegexProcessor:

    @staticmethod
    def _handle_escapes(regex: str) -> Tuple[str, Dict[str, str]]:
        """
        Substitui sequências de escape (e.g., '\(', '\*') por caracteres placeholder
        de uso privado para que não sejam processados como operadores.

        Retorna a regex processada e um mapa do placeholder para o caractere original.
        """
        processed_regex = []
        placeholder_map: Dict[str, str] = {}
        # Usamos a Área de Uso Privado do Unicode para placeholders seguros
        next_placeholder_code = 0xE000 
        
        i = 0
        n = len(regex)
        while i < n:
            if regex[i] == '\\' and i + 1 < n:
                original_char = regex[i + 1]
                
                # Verifica se já existe um placeholder para este caractere
                # Isso é ineficiente, mas mais simples. Para otimizar, poderíamos usar um mapa reverso.
                found_placeholder = None
                for p, o_char in placeholder_map.items():
                    if o_char == original_char:
                        found_placeholder = p
                        break
                
                if found_placeholder:
                    placeholder = found_placeholder
                else:
                    placeholder = chr(next_placeholder_code)
                    placeholder_map[placeholder] = original_char
                    next_placeholder_code += 1

                processed_regex.append(placeholder)
                i += 2  # Pula o caractere de escape e o caractere escapado
            else:
                processed_regex.append(regex[i])
                i += 1
                
        return "".join(processed_regex), placeholder_map
    
    @staticmethod
    def _expand_char_classes(regex: str) -> str:
        """
        Transforma expressões de classe de caracteres como [a-zA-Z0-9] em
        (a|b|...|z|A|B|...|Z|0|1|...|9). Suporta múltiplos intervalos e caracteres isolados.
        """
        i = 0
        expanded = []
        n = len(regex)

        while i < n:
            if regex[i] == '[':
                j = i + 1
                while j < n and regex[j] != ']':
                    j += 1
                if j >= n:
                    raise ValueError(f"Char class was not closed in: {regex[i:]}")
                class_body = regex[i+1:j]
                chars = []
                k = 0
                while k < len(class_body):
                    if (k + 2 < len(class_body)) and (class_body[k+1] == '-'):
                        start_char = class_body[k]
                        end_char = class_body[k+2]
                        for code in range(ord(start_char), ord(end_char) + 1):
                            chars.append(chr(code))
                        k += 3
                    else:
                        chars.append(class_body[k])
                        k += 1
                seen = set()
                unique_chars = []
                for c in chars:
                    if c not in seen:
                        seen.add(c)
                        unique_chars.append(c)
                union_expr = "(" + "|".join(unique_chars) + ")"
                expanded.append(union_expr)
                i = j + 1
            else:
                expanded.append(regex[i])
                i += 1

        return "".join(expanded)

    @staticmethod
    def _preprocess_regex(regex: str, literal_placeholders: Set[str]) -> str:
        """Adiciona '.' entre operadores. Placeholders são tratados como literais."""
        processed_regex = []
        if not regex:
            return ""
        for i, char in enumerate(regex):
            processed_regex.append(char)
            if i < len(regex) - 1:
                next_char = regex[i+1]
                
                is_char_operand = char.isalnum() or char in literal_placeholders
                is_next_char_operand = next_char.isalnum() or next_char in literal_placeholders

                if (is_char_operand or char in '*?+)') and \
                   (is_next_char_operand or next_char == '('):
                    processed_regex.append('.')
        return "".join(processed_regex)

    @staticmethod
    def _parse_regex_to_postfix(regex: str, literal_placeholders: Set[str]) -> str:
        """Converte para postfix. Placeholders são tratados como literais."""
        if not regex:
            return ""

        postfix: List[str] = []
        op_stack: List[str] = []
        precedence: Dict[str, int] = {'|': 1, '.': 2, '*': 3, '?': 3, '+': 3}

        for token in regex:
            if token.isalnum() or token == '#' or token in literal_placeholders:
                postfix.append(token)
            elif token == '(':
                op_stack.append(token)
            elif token == ')':
                while op_stack and op_stack[-1] != '(':
                    postfix.append(op_stack.pop())
                if not op_stack or op_stack[-1] != '(':
                    raise ValueError("Mismatched parentheses")
                op_stack.pop()
            else:
                while (op_stack and op_stack[-1] != '(' and
                       precedence.get(op_stack[-1], 0) >= precedence.get(token, 0)):
                    postfix.append(op_stack.pop())
                op_stack.append(token)
        
        while op_stack:
            if op_stack[-1] == '(':
                raise ValueError("Mismatched parentheses")
            postfix.append(op_stack.pop())
        return "".join(postfix)

    @staticmethod
    def _build_syntax_tree(
        postfix_regex: str,
        placeholder_map: Dict[str, str]
    ) -> Tuple[Optional[SyntaxTreeNode], Dict[int, str], Set[str], Optional[int]]:

        SyntaxTreeNode._position_counter = 1
        stack: List[SyntaxTreeNode] = []
        symbols_map: Dict[int, str] = {}
        alphabet: Set[str] = set()
        end_marker_pos: Optional[int] = None

        if not postfix_regex:
            return None, symbols_map, alphabet, end_marker_pos

        for token in postfix_regex:
            is_literal = token.isalnum()
            is_placeholder = token in placeholder_map

            if is_literal or is_placeholder:
                original_value = placeholder_map.get(token, token)
                node = SyntaxTreeNode('LITERAL', value=original_value)
                if node.position is not None:
                    symbols_map[node.position] = original_value
                alphabet.add(original_value)
                stack.append(node)
            elif token == '#': # End marker
                node = SyntaxTreeNode('ENDMARKER', value='#')
                if node.position is not None:
                    symbols_map[node.position] = '#'
                    end_marker_pos = node.position
                stack.append(node)
            elif token == '.':
                if len(stack) < 2: raise ValueError("Invalid postfix for concatenation")
                c2, c1 = stack.pop(), stack.pop()
                stack.append(SyntaxTreeNode('CONCAT', children=[c1, c2]))
            elif token == '|':
                if len(stack) < 2: raise ValueError("Invalid postfix for union")
                c2, c1 = stack.pop(), stack.pop()
                stack.append(SyntaxTreeNode('UNION', children=[c1, c2]))
            elif token == '*':
                if len(stack) < 1: raise ValueError("Invalid postfix for Kleene star")
                c1 = stack.pop()
                stack.append(SyntaxTreeNode('STAR', children=[c1]))
            elif token == '+':
                if len(stack) < 1: raise ValueError("Invalid postfix for Plus")
                c1 = stack.pop()
                stack.append(SyntaxTreeNode('PLUS', children=[c1]))
            elif token == '?':
                if len(stack) < 1: raise ValueError("Invalid postfix for Option")
                c1 = stack.pop()
                stack.append(SyntaxTreeNode('OPTION', children=[c1]))
            else:
                raise ValueError(f"Unknown token in postfix regex: {token}")

        if len(stack) != 1:
            raise ValueError("Invalid postfix regex, stack should have 1 element (root node)")
        
        return stack[0], symbols_map, alphabet, end_marker_pos

    @staticmethod
    def _compute_tree_annotations(node: Optional[SyntaxTreeNode]):
        """Computa nullable, firstpos e lastpos para cada nó da árvore recursivamente."""
        if node is None:
            return

        for child in node.children:
            RegexProcessor._compute_tree_annotations(child)

        if node.node_type == 'LITERAL' or node.node_type == 'ENDMARKER':
            node.nullable = False
            if node.position is not None:
                node.firstpos = {node.position}
                node.lastpos = {node.position}
        elif node.node_type == 'EPSILON':
            node.nullable = True
            node.firstpos = set()
            node.lastpos = set()
        elif node.node_type == 'CONCAT':
            c1, c2 = node.children[0], node.children[1]
            node.nullable = c1.nullable and c2.nullable
            node.firstpos = c1.firstpos.copy()
            if c1.nullable:
                node.firstpos.update(c2.firstpos)
            node.lastpos = c2.lastpos.copy()
            if c2.nullable:
                node.lastpos.update(c1.lastpos)
        elif node.node_type == 'UNION':
            c1, c2 = node.children[0], node.children[1]
            node.nullable = c1.nullable or c2.nullable
            node.firstpos = c1.firstpos.union(c2.firstpos)
            node.lastpos = c1.lastpos.union(c2.lastpos)
        elif node.node_type == 'STAR': # c*
            c1 = node.children[0]
            node.nullable = True
            node.firstpos = c1.firstpos.copy()
            node.lastpos = c1.lastpos.copy()
        elif node.node_type == 'PLUS': # c+
            c1 = node.children[0]
            node.nullable = c1.nullable
            node.firstpos = c1.firstpos.copy()
            node.lastpos = c1.lastpos.copy()
        elif node.node_type == 'OPTION': # c?
            c1 = node.children[0]
            node.nullable = True
            node.firstpos = c1.firstpos.copy()
            node.lastpos = c1.lastpos.copy()


    @staticmethod
    def _compute_followpos(
        node: Optional[SyntaxTreeNode], 
        followpos_table: Dict[int, Set[int]]
    ) -> None:
        """ Computa o followpos para cada nó da árvore recursivamente. """
        if node is None:
            return

        for child in node.children:
            RegexProcessor._compute_followpos(child, followpos_table)

        if node.node_type == 'CONCAT':
            c1, c2 = node.children[0], node.children[1]
            for i in c1.lastpos:
                followpos_table.setdefault(i, set()).update(c2.firstpos)

        elif node.node_type == 'STAR':
            c1 = node.children[0]
            for i in c1.lastpos:
                followpos_table.setdefault(i, set()).update(c1.firstpos)

        elif node.node_type == 'PLUS':
            c1 = node.children[0]
            for i in c1.lastpos:
                followpos_table.setdefault(i, set()).update(c1.firstpos)


    @staticmethod
    def regex_to_dfa(regex: str) -> DeterministicFiniteAutomata:
        """Converte uma expressão regular em um autômato finito determinístico (DFA)."""
        
        # 0a. Lida com sequências de escape, substituindo-as por placeholders
        escaped_regex, placeholder_map = RegexProcessor._handle_escapes(regex)
        literal_placeholders = set(placeholder_map.keys())

        # 0b. Expande classes de caracteres [a-zA-Z0-9] para uniões explícitas
        if escaped_regex:
            try:
                expanded_regex = RegexProcessor._expand_char_classes(escaped_regex)
            except ValueError as e:
                raise ValueError(f"Error to expand char classes '{regex}': {e}")
        else:
            expanded_regex = ""
        
        print("Processed Regex (with placeholders and expansions):", expanded_regex)

        # Trata o caso de regex vazia
        if not expanded_regex:
            q_empty_accept = "D0"
            return DeterministicFiniteAutomata(
                states={q_empty_accept}, alphabet=set(), transitions={},
                start_state=q_empty_accept, accept_states={q_empty_accept}
            )

        # 1. Preprocessa a expressão regular (adiciona '.')
        preprocessed_regex = RegexProcessor._preprocess_regex(expanded_regex, literal_placeholders)
        if not preprocessed_regex:
             q_empty_accept = "D0"
             return DeterministicFiniteAutomata(
                 states={q_empty_accept}, alphabet=set(), transitions={},
                 start_state=q_empty_accept, accept_states={q_empty_accept}
             )

        # Converte para postfix
        postfix_original = RegexProcessor._parse_regex_to_postfix(preprocessed_regex, literal_placeholders)
        if not postfix_original:
            q_empty_accept = "D0"
            return DeterministicFiniteAutomata(
                states={q_empty_accept}, alphabet=set(), transitions={},
                start_state=q_empty_accept, accept_states={q_empty_accept}
            )
            
        augmented_postfix = postfix_original + "#" + "."

        try:
            # 2. Constrói a árvore sintática
            root, symbols_map, alphabet, end_marker_pos = \
                RegexProcessor._build_syntax_tree(augmented_postfix, placeholder_map)

            if root is None or end_marker_pos is None:
                raise ValueError("Failed to build syntax tree or find end marker.")

            # 3. Computa nullable, firstpos, lastpos
            RegexProcessor._compute_tree_annotations(root)

            # 4. Computa a tabela de followpos
            num_positions = SyntaxTreeNode._position_counter 
            followpos_table: Dict[int, Set[int]] = {i: set() for i in range(1, num_positions)}
            RegexProcessor._compute_followpos(root, followpos_table)

            # 5. Constrói DFA
            dfa_states: Set[str] = set()
            dfa_transitions: Dict[Tuple[str, str], str] = {}
            dfa_accept_states: Set[str] = set()
            
            dfa_state_name_map: Dict[FrozenSet[int], str] = {}
            next_dfa_state_id = 0

            def get_dfa_name(pos_set: FrozenSet[int]) -> str:
                nonlocal next_dfa_state_id
                if pos_set not in dfa_state_name_map:
                    name = f"D{next_dfa_state_id}"
                    dfa_state_name_map[pos_set] = name
                    next_dfa_state_id += 1
                return dfa_state_name_map[pos_set]

            initial_pos_set = frozenset(root.firstpos)
            if not initial_pos_set: # Lida com linguagem vazia ou que aceita apenas a string vazia
                d0_name = get_dfa_name(initial_pos_set)
                dfa_states.add(d0_name)
                start_state = d0_name
                accept_states = {d0_name} if root.nullable else set()
                return DeterministicFiniteAutomata(
                    states=dfa_states, alphabet=alphabet, transitions=dfa_transitions,
                    start_state=start_state, accept_states=accept_states
                )

            dfa_start_state_name = get_dfa_name(initial_pos_set)
            dfa_states.add(dfa_start_state_name)

            unprocessed_dfa_states: List[FrozenSet[int]] = [initial_pos_set]
            processed_dfa_sets: Set[FrozenSet[int]] = set()

            while unprocessed_dfa_states:
                current_pos_frozenset = unprocessed_dfa_states.pop(0)
                if current_pos_frozenset in processed_dfa_sets:
                    continue
                processed_dfa_sets.add(current_pos_frozenset)
                
                current_dfa_name = get_dfa_name(current_pos_frozenset)

                if end_marker_pos in current_pos_frozenset:
                    dfa_accept_states.add(current_dfa_name)

                for char_symbol in alphabet:
                    next_positions_union: Set[int] = set()
                    for pos in current_pos_frozenset:
                        if symbols_map.get(pos) == char_symbol:
                            next_positions_union.update(followpos_table.get(pos, set()))
                    
                    if next_positions_union:
                        next_dfa_pos_frozenset = frozenset(next_positions_union)
                        next_dfa_name = get_dfa_name(next_dfa_pos_frozenset)
                        dfa_states.add(next_dfa_name)
                        dfa_transitions[(current_dfa_name, char_symbol)] = next_dfa_name
                        
                        if next_dfa_pos_frozenset not in processed_dfa_sets:
                            unprocessed_dfa_states.append(next_dfa_pos_frozenset)
            
            return DeterministicFiniteAutomata(
                states=dfa_states,
                alphabet=alphabet,
                transitions=dfa_transitions,
                start_state=dfa_start_state_name,
                accept_states=dfa_accept_states
            )

        except ValueError as e:
            raise ValueError(f"Falha ao processar regex '{regex}': {e}")
