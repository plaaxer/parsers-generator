from src.scanner_framework.automatas.non_deterministic_automata import NonDeterministicFiniteAutomata
from src.scanner_framework.automatas.deterministic_automata import DeterministicFiniteAutomata



class LexicalAnalyzer():
    DEFAULT_PREFIX_SEPARATOR = "::"  # Used for state renaming

    def __init__(self, name, application):
        self.name = name
        self.application = application
        self.dfas = {}
        self.nfa = None
        self.dfa = None
        self.dfa_accept_state_to_token_type_map = {}
        self.has_errors = False

    def add_dfa(self, key, dfa):
        """
        Adds a DFA for a specific token pattern.
        key: The token type string (e.g., "ID", "NUMBER", "KEYWORD_IF")
        dfa: The DeterministicFiniteAutomata object for this pattern.
        """
        if key in self.dfas:
            self.application.error(f"DFA com key {key} já existe.")
            return

        self.dfas[key] = dfa

    def generate(self):
        """
        Generates the final DFA for the lexical analyzer by:
        1. Uniting all registered DFAs into a single NFA using epsilon transitions.
        2. Determinizing the resulting NFA.
        """
        try:
            if not self.dfas:
                self.application.error(
                    "Nenhum DFA foi adicionado para gerar o analisador léxico.")
                self.has_errors = True
                return

            self.unite_by_epsilon()
            if self.has_errors:
                return

            self.determinize()
            if self.has_errors:
                return

            print("DFA Final Gerado:")
            print(self.dfa)

        except Exception as e:
            self.application.error(
                f"Falha fatal ao gerar o analisador léxico: {e}")
            self.has_errors = True

    def unite_by_epsilon(self):
        """
        Unites all DFAs in self.dfas into a single NFA (self.nfa)
        using a new start state and epsilon transitions to the start states
        of the original DFAs. States are renamed to ensure uniqueness.
        """
        new_states = set()
        new_alphabet = set()
        new_transitions = {}
        new_accept_states = set()

        new_start_state = "S0_NFA_UNION"
        new_states.add(new_start_state)

        if not self.dfas:
            self.application.error("Nenhum DFA para unir.")
            self.has_errors = True
            return

        for key, dfa_orig in self.dfas.items():
            if not dfa_orig or not hasattr(dfa_orig, 'states'):
                self.application.error(
                    f"DFA inválido para a chave '{key}'. Pulando.")
                continue

            prefix = f"{key}{self.DEFAULT_PREFIX_SEPARATOR}"

            state_mapping = {state: prefix +
                             str(state) for state in dfa_orig.states}

            renamed_dfa_states = set(state_mapping.values())
            new_states.update(renamed_dfa_states)

            new_alphabet.update(dfa_orig.alphabet)

            for acc_state in dfa_orig.accept_states:
                new_accept_states.add(state_mapping[acc_state])

            for (from_state_orig, symbol), target_state_orig in dfa_orig.transitions.items():
                renamed_from = state_mapping[from_state_orig]
                renamed_target = state_mapping[target_state_orig]

                if (renamed_from, symbol) not in new_transitions:
                    new_transitions[(renamed_from, symbol)] = set()
                new_transitions[(renamed_from, symbol)].add(renamed_target)

            renamed_dfa_start_state = state_mapping[dfa_orig.start_state]
            if (new_start_state, NonDeterministicFiniteAutomata.EPSILON) not in new_transitions:
                new_transitions[(
                    new_start_state, NonDeterministicFiniteAutomata.EPSILON)] = set()
            new_transitions[(new_start_state, NonDeterministicFiniteAutomata.EPSILON)].add(
                renamed_dfa_start_state)

        self.nfa = NonDeterministicFiniteAutomata(
            states=new_states,
            alphabet=new_alphabet,
            transitions=new_transitions,
            start_state=new_start_state,
            accept_states=new_accept_states
        )

    def determinize(self):
        """
        Converts the NFA (self.nfa) to an equivalent DFA (self.dfa)
        using the subset construction algorithm.
        It also populates self.dfa_accept_state_to_token_type_map.
        """
        nfa = self.nfa
        if not nfa:
            self.application.error("NFA não existe para determinização.")
            self.has_errors = True
            return

        start_closure = frozenset(nfa._epsilon_closure({nfa.start_state}))

        dfa_states = {start_closure}
        dfa_transitions = {}

        self.dfa_accept_state_to_token_type_map.clear()

        token_type_priority = {key: i for i,
                               key in enumerate(self.dfas.keys())}

        unmarked_dfa_states = [start_closure]

        while unmarked_dfa_states:
            current_dfa_state_T = unmarked_dfa_states.pop(0)

            possible_tokens_for_T = {}
            for nfa_state_name in current_dfa_state_T:
                if nfa_state_name in nfa.accept_states:
                    token_key = nfa_state_name.split(
                        self.DEFAULT_PREFIX_SEPARATOR, 1)[0]
                    if token_key in self.dfas:
                        priority = token_type_priority.get(
                            token_key, float('inf'))
                        if token_key not in possible_tokens_for_T or priority < possible_tokens_for_T[token_key]:
                            possible_tokens_for_T[token_key] = priority

            if possible_tokens_for_T:
                best_token_key = min(possible_tokens_for_T,key=possible_tokens_for_T.get)
                self.dfa_accept_state_to_token_type_map[current_dfa_state_T] = best_token_key

            for symbol in nfa.alphabet:
                if symbol == NonDeterministicFiniteAutomata.EPSILON:
                    continue

                nfa_states_after_move = set()
                for q_nfa in current_dfa_state_T:
                    nfa_states_after_move.update(
                        nfa.transitions.get((q_nfa, symbol), set()))

                if not nfa_states_after_move:
                    continue

                target_dfa_state_U = frozenset(
                    nfa._epsilon_closure(nfa_states_after_move))
                if not target_dfa_state_U:
                    continue

                dfa_transitions[(current_dfa_state_T, symbol)
                                ] = target_dfa_state_U

                if target_dfa_state_U not in dfa_states:
                    dfa_states.add(target_dfa_state_U)
                    unmarked_dfa_states.append(target_dfa_state_U)

        dfa_actual_accept_states = set(
            self.dfa_accept_state_to_token_type_map.keys())

        dfa_alphabet = {s for s in nfa.alphabet if s !=
                        NonDeterministicFiniteAutomata.EPSILON}

        self.dfa = DeterministicFiniteAutomata(
            states=dfa_states,
            alphabet=dfa_alphabet,
            transitions=dfa_transitions,
            start_state=start_closure,
            accept_states=dfa_actual_accept_states
        )

    def process(self, input_stream):
        """
        Processes the input_stream using the generated DFA to produce a list of tokens.
        Each token is a tuple: (lexeme, token_type) or (lexeme, "erro!").
        Whitespace between tokens is skipped unless defined as a token itself.
        """
        if self.has_errors or not self.dfa:
            self.application.error(
                "Analisador léxico não foi gerado ou contém erros. Não é possível processar.")
            return []

        if not self.dfa_accept_state_to_token_type_map:

            if self.dfa.accept_states:
                self.application.error(
                    "Crítico: Mapa de estados de aceitação para tipos de token está vazio, mas DFA tem estados de aceitação.")

            self.application.warning(
                "Aviso: Mapa de estados de aceitação para tipos de token está vazio.")

        tokens = []
        current_pos = 0
        input_len = len(input_stream)

        while current_pos < input_len:
            # 1. Skip inter-token whitespace (if whitespace is not a token itself)
            # This assumes whitespace is not part of any token definition.
            # If 'WS' is a token type, this explicit skip should be removed or conditional.
            start_of_potential_token = current_pos
            while current_pos < input_len and input_stream[current_pos].isspace():
                current_pos += 1

            if current_pos == start_of_potential_token and current_pos == input_len:  # Only whitespace and now EOF
                break
            if current_pos == input_len and current_pos > start_of_potential_token:  # Skipped whitespace to EOF
                break

            # 2. Maximal Munch: Find the longest possible lexeme from current_pos
            current_dfa_state = self.dfa.start_state
            current_lexeme_scan = ""

            # Store the last recognized valid lexeme and its state info
            # (lexeme_str, dfa_accept_state_frozenset, position_after_lexeme)
            last_accepted_lexeme_info = None

            scan_pos = current_pos
            while scan_pos < input_len:
                char = input_stream[scan_pos]

                # If char is whitespace and we are configured to stop tokens at whitespace
                # (and whitespace is not part of the current token pattern e.g. string literal)
                # For simplicity, this example assumes patterns don't cross whitespace unless whitespace is in their alphabet.
                # The DFA transition handles this naturally if whitespace is in alphabet.
                # If not, and a pattern could accept whitespace, this logic might be too simple.

                next_dfa_state = self.dfa.transitions.get(
                    (current_dfa_state, char))

                if next_dfa_state is not None:
                    current_lexeme_scan += char
                    current_dfa_state = next_dfa_state
                    scan_pos += 1

                    # Check if the current_dfa_state is an accept state
                    if current_dfa_state in self.dfa.accept_states:  # dfa.accept_states are frozensets
                        last_accepted_lexeme_info = (
                            current_lexeme_scan, current_dfa_state, scan_pos)
                else:
                    # No transition for 'char' from 'current_dfa_state'
                    break  # End of current scan for maximal munch

            # 3. Process the found lexeme or handle error
            if last_accepted_lexeme_info:
                final_lexeme, final_dfa_accept_state, next_pos_after_lexeme = last_accepted_lexeme_info

                # Determine base token type from the DFA accept state map
                base_token_type = self.dfa_accept_state_to_token_type_map.get(
                    final_dfa_accept_state)

                if not base_token_type:
                    # This is a serious issue if an accept state is not in the map.
                    # It implies a flaw in the determinize/map population logic.
                    tokens.append(
                        (final_lexeme, "erro!_TIPO_INTERNO_DESCONHECIDO"))
                    self.application.error(
                        f"Erro Interno: Lexema '{final_lexeme}' aceito pelo estado {final_dfa_accept_state} que não está no mapa de tipos.")
                # else:
                #     # Check symbol table for reserved words/specific lexemes
                #     # This allows "if" (base_token_type 'ID') to become 'PR_IF'
                #     overriding_token_type = self.application.symbol_table.lookup(final_lexeme)
                #     if overriding_token_type:
                #         # Potentially add a check: is base_token_type compatible with being overridden?
                #         # e.g., an 'ID' can be a keyword, a 'NUMBER' typically cannot.
                #         # For now, assume symbol table lookup takes precedence if valid.
                #         tokens.append((final_lexeme, overriding_token_type))
                #     else:
                #         tokens.append((final_lexeme, base_token_type))

                current_pos = next_pos_after_lexeme  # Advance main pointer

            else:  # nenhum lexema válido encontrado começando de current_pos
                if current_pos < input_len:  # ter certeza de que ainda há caracteres para processar
                    error_char = input_stream[current_pos]
                    tokens.append((error_char, "erro!"))
                    self.application.log(
                        f"Erro Léxico: Caractere inesperado '{error_char}' na posição {current_pos}.")
                    current_pos += 1  # ignora o caractere inválido e avança

        return tokens

    def get_info(self):
        return f"Analisador Léxico: {self.name}, DFAs Registrados: {len(self.dfas)}"
