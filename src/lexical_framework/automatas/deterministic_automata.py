from src.lexical_framework.automatas.automata import Automata

class DeterministicFiniteAutomata(Automata):
    def __init__(self, states, alphabet, transitions, start_state, accept_states):

        super().__init__(states, alphabet, transitions, start_state, accept_states)

    def process(self, input_string) -> bool:

        self.reset()

        for symbol in input_string:
            if symbol not in self.alphabet:
                return False

            transition_key = (self.current_state, symbol)
            if transition_key not in self.transitions:
                return False

            self.current_state = self.transitions[transition_key]

        return self.is_accepting(self.current_state)

    def __str__(self):
        def fmt_state(s):
            if isinstance(s, frozenset):
                return "{" + ", ".join(sorted(s)) + "}"
            return str(s)

        result = []
        result.append("DeterministicFiniteAutomata:")
        result.append(f"  States: {[fmt_state(s) for s in self.states]}")
        result.append(f"  Alphabet: {sorted(self.alphabet)}")
        result.append("  Transitions:")
        for (state, symbol), target in self.transitions.items():
            result.append(f"    δ({fmt_state(state)}, '{symbol}') → {fmt_state(target)}")
        result.append(f"  Start State: {fmt_state(self.start_state)}")
        result.append(f"  Accept States: {[fmt_state(s) for s in self.accept_states]}")
        return "\n".join(result)

    def __repr__(self):
        return self.__str__()

    def _format_transitions(self):
        return {f"{state},'{symbol}'": next_state for (state, symbol), next_state in self.transitions.items()}

    def to_file_format(self) -> str:
        lines = []

        lines.append(str(len(self.states)))

        lines.append(str(self.start_state))

        lines.append(','.join(str(state) for state in self.accept_states))

        lines.append(','.join(str(symbol) for symbol in self.alphabet))

        for (state, symbol), next_state in self.transitions.items():
            lines.append(f"{state},{symbol},{next_state}")

        return '\n'.join(lines)
