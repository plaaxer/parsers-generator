from src.scanner_framework.automatas.automata import Automata

class NonDeterministicFiniteAutomata(Automata):
    EPSILON = '&'  # Convention for representing epsilon transitions

    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        """
        Initializes a Non-Deterministic Finite Automaton.
        Args:
            states (iterable): A collection of states.
            alphabet (iterable): A collection of input symbols (should not include EPSILON).
            transitions (dict): A dictionary representing the transition function.
                                 Keys are tuples (current_state, symbol_or_EPSILON),
                                 Values are sets of next_states.
                                 Example: {('q0', '0'): {'q0', 'q1'}, ('q1', EPSILON): {'q2'}}
            start_state: The starting state.
            accept_states (iterable): A collection of accept states.
        """
        super().__init__(states, alphabet, transitions, start_state, accept_states)
        # NFA tracks a set of active states.
        self.active_states = set()
        # The self.current_state attribute from the base class is not used by this NFA's logic.

    def _epsilon_closure(self, input_states):
        """
        Computes the epsilon closure for a given set of states.
        Args:
            input_states (set): A set of states.
        Returns:
            set: The set of states reachable from input_states via epsilon transitions.
        """
        if not isinstance(input_states, set):
            raise TypeError("Input states must be a set.")

        closure = set(input_states)
        worklist = list(input_states) # Use a list as a queue/stack

        while worklist:
            current_s = worklist.pop(0)  # Process states FIFO for clarity, though order doesn't strictly matter for closure
            
            # Get states reachable by an epsilon transition
            epsilon_moves = self.transitions.get((current_s, self.EPSILON), set())
            
            for state in epsilon_moves:
                if state not in closure:
                    closure.add(state)
                    worklist.append(state)
        return closure

    def reset(self):
        """
        Resets the NFA to its initial configuration.
        The active states become the epsilon closure of the start state.
        This overrides the base class's reset method.
        """
        self.active_states = self._epsilon_closure({self.start_state})

    def process(self, input_string):
        """
        Processes an input string and determines if the NFA accepts it.
        Args:
            input_string (str): The string to process.
        Returns:
            bool: True if the string is accepted, False otherwise.
        """
        self.reset()  # Initialize active_states

        for symbol in input_string:
            if symbol not in self.alphabet:
                # Symbol is not in the NFA's input alphabet
                # Note: self.EPSILON is not expected in the input_string
                return False  # Reject the string

            next_states_after_symbol = set()
            for state in self.active_states:
                # Get states reachable by consuming the current symbol
                symbol_moves = self.transitions.get((state, symbol), set())
                next_states_after_symbol.update(symbol_moves)
            
            # If no states can be reached by the current symbol from any currently active state,
            # then this path of computation dies.
            # The epsilon closure of an empty set is an empty set.
            self.active_states = self._epsilon_closure(next_states_after_symbol)

            if not self.active_states:
                # If, after processing the symbol and taking epsilon closures,
                # there are no active states, the NFA is stuck.
                return False 

        # After processing the entire string, check if any of the active states are accept states
        for state in self.active_states:
            if self.is_accepting(state): # Uses base class's is_accepting method
                return True
        
        return False # No active state is an accept state

    def __str__(self):
        def fmt_state(state):
            if isinstance(state, frozenset):
                return "{" + ", ".join(sorted(state)) + "}"
            return str(state)

        def fmt_transitions():
            lines = []
            for (state, symbol), targets in sorted(self.transitions.items(), key=lambda item: (fmt_state(item[0][0]), item[0][1])):
                targets_str = ", ".join(sorted(targets))
                lines.append(f"    δ({fmt_state(state)}, '{symbol}') → {{{targets_str}}}")
            return "\n".join(lines)

        lines = [
            "NonDeterministicFiniteAutomata:",
            "  States:",
        ]
        for state in sorted(self.states, key=lambda s: sorted(s) if isinstance(s, frozenset) else s):
            lines.append(f"    {fmt_state(state)}")

        lines.append("  Alphabet:")
        for symbol in sorted(self.alphabet):
            lines.append(f"    '{symbol}'")

        lines.append("  Transitions:")
        lines.append(fmt_transitions())

        lines.append(f"  Start State:\n    {fmt_state(self.start_state)}")

        lines.append("  Accept States:")
        for state in sorted(self.accept_states, key=lambda s: sorted(s) if isinstance(s, frozenset) else s):
            lines.append(f"    {fmt_state(state)}")

        return "\n".join(lines)

    def _format_transitions(self):
        lines = ["{"]
        for (state, symbol), targets in sorted(self.transitions.items()):
            targets_str = ', '.join(sorted(targets))
            lines.append(f"    ({state!r}, {symbol!r}): {{{targets_str}}},")
        lines.append("  }")
        return '\n'.join(lines)
