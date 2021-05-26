import copy

from automata.base.exceptions import RejectionException
from automata.fa.dfa import DFA


class WDFA(DFA):
    """A weighted deterministic finite automaton."""

    def __init__(self, *, states, input_symbols, transitions, initial_state, final_states, weights):
        """Initialize a complete WDFA."""
        super().__init__(states=states, input_symbols=input_symbols, transitions=transitions, initial_state=initial_state, final_states=final_states)
        self.weights = copy.deepcopy(weights)
        self.accumulated_cost = 0

    def read_input_stepwise(self, input_str):
        """
        Check if the given string is accepted by this WDFA.
        Yield the current configuration of the WDFA at each step.
        Compute the path cost
        """
        current_state = self.initial_state

        yield current_state, 0
        for input_symbol in input_str:
            current_state, cost = self._get_next_current_state(current_state, input_symbol)
            self.accumulated_cost += cost
            yield current_state, self.accumulated_cost

        self._check_for_input_rejection(current_state)

    def _get_next_current_state(self, current_state, input_symbol):
        """
        Follow the transition for the given input symbol on the current state.
        Raise an error if the transition does not exist.
        """
        if input_symbol in self.transitions[current_state]:
            return self.transitions[current_state][input_symbol], self.weights[current_state][input_symbol]
        else:
            raise RejectionException('{} is not a valid input symbol'.format(input_symbol))

    def reset(self):
        self.accumulated_cost = 0


if __name__ == '__main__':
    wdfa = WDFA(
        states={'q0', 'fu', 'te', 'va'},
        input_symbols={'f', 't', 'v'},
        transitions={
            'q0': {'f': 'fu', 't': 'te', 'v': 'va'},
            'fu': {'f': 'fu', 't': 'te', 'v': 'va'},
            'te': {'f': 'fu', 't': 'te', 'v': 'va'},
            'va': {'f': 'fu', 't': 'te', 'v': 'va'},
        },
        weights={
                'q0': {'f': 4, 't': 0, 'v': 5},
                'fu': {'f': 2, 't': 1, 'v': 1},
                'te': {'f': 1, 't': 0, 'v': 6},
                'va': {'f': 2, 't': 1, 'v': 2}
        },
        initial_state='q0',
        final_states={'va'})

    print(wdfa.read_input('tfv'))
