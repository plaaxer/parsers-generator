class Automata:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions  # Should be defined by subclasses
        self.start_state = start_state
        self.accept_states = set(accept_states)

    def is_accepting(self, state):
        return state in self.accept_states

    def reset(self):
        self.current_state = self.start_state

    def process(self, input_string):
        raise NotImplementedError("Subclasses should implement this method.")