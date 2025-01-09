from typing import Dict, List, Tuple, Optional, Union, Sequence
import numpy as np
import pickle
import os

class NHLMarkovModel:
    """A Markov model for analyzing NHL game states and transitions.

    This class implements a Markov chain model for analyzing hockey game states,
    tracking transitions between different game situations defined by score,
    game situation codes, and location on the ice.

    Attributes:
        score_range (range): Range of possible score differentials (-6 to 6).
        situations (List[int]): Valid game situation codes.
        locations (List[str]): Valid locations on ice ('O', 'N', 'D').
        states (Dict[Tuple[int, int, str], int]): Mapping of game states to indices.
        n_states (int): Total number of possible states.
        transitions (np.ndarray): Matrix of transition probabilities between states.
        is_normalized (bool): Whether transition probabilities have been normalized.
    """
    def __init__(self) -> None:
        """Initialize the NHL Markov Model with predefined states and transitions."""
        self.score_range = range(-6, 7)
        self.situations = [641, 1460,
                            651, 1560,
                            1541, 1451,
                            1551,
                            1550, 551, 
                            1531, 1351,
                            541, 1450,
                            531, 1350,
                            1441,
                            1431, 1341,
                            1331
                            ]
        self.locations = ['O','N','D']
        
        self.states: Dict[Tuple[int, int, str], int] = {}
        idx = 0
        for score in self.score_range:
            for sit in self.situations:
                for loc in self.locations:
                    self.states[(score, sit, loc)] = idx
                    idx += 1
        
        self.n_states = len(self.states)
        self.transitions = np.zeros((self.n_states, self.n_states))
        self.is_normalized = False
    
    def state_to_idx(self, score: int, situation: int, location: str) -> Optional[int]:
        """Convert a game state to its corresponding index.

        Args:
            score (int): Score differential.
            situation (int): Game situation code.
            location (str): Location on ice ('O', 'N', or 'D').

        Returns:
            Optional[int]: Index of the state in the transition matrix, or None if invalid.
        """
        return self.states.get((score, situation, location))
    
    def update_transitions(self, goals: Sequence[int], situations: Sequence[int], locations: Sequence[str]) -> None:
        """Update transition counts based on observed game sequences.

        Args:
            goals (Sequence[int]): Sequence of score differentials.
            situations (Sequence[int]): Sequence of game situation codes.
            locations (Sequence[str]): Sequence of locations on ice.

        Note:
            This method updates the raw transition counts and sets is_normalized to False.
            Call normalize() to convert counts to probabilities.
        """
        for t in range(len(goals) - 1):
            current_state = self.state_to_idx(goals[t], situations[t], locations[t])
            next_state = self.state_to_idx(goals[t+1], situations[t+1], locations[t+1])
            if current_state is not None and next_state is not None:
                self.transitions[current_state, next_state] += 1
        self.is_normalized = False
    
    def normalize(self) -> None:
        """Normalize transition counts to probabilities.

        Converts the raw transition counts to probabilities by dividing each row
        by its sum. Rows that sum to zero are left unchanged to avoid division
        by zero.
        """
        row_sums = self.transitions.sum(axis=1)
        mask = row_sums > 0
        self.transitions[mask] = self.transitions[mask] / row_sums[mask, np.newaxis]
        self.is_normalized = True

    def propagate(self, initial_score: int, initial_situation: int, initial_location: str, n_steps: int) -> np.ndarray:
        """Compute state probabilities after n steps from an initial state.

        Args:
            initial_score (int): Initial score differential.
            initial_situation (int): Initial game situation code.
            initial_location (str): Initial location on ice.
            n_steps (int): Number of steps to propagate forward.

        Returns:
            np.ndarray: Array of probabilities for each state after n_steps.

        Raises:
            ValueError: If the initial state is invalid.
        """
        if not self.is_normalized:
            self.normalize()
            
        current_state = self.state_to_idx(initial_score, initial_situation, initial_location)
        if current_state is None:
            raise ValueError("Invalid initial state")
        
        state_probabilities = np.zeros(self.n_states)
        state_probabilities[current_state] = 1.0

        if os.path.exists(f"matrices/{n_steps}.npy"):
            matrix = np.load(f"matrices/{n_steps}.npy")
        else:
            matrix = np.linalg.matrix_power(self.transitions, n_steps)
            np.save(f"matrices/{n_steps}.npy", matrix)
        
        final_probabilities = state_probabilities @ matrix
        return final_probabilities
    
    def save(self, filepath: str) -> None:
        """Save the model to a file.

        Args:
            filepath (str): Path where the model should be saved.
        """
        with open(filepath, 'wb') as f:
            pickle.dump({
                'transitions': self.transitions,
                'is_normalized': self.is_normalized,
                'states': self.states
            }, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'NHLMarkovModel':
        """Load a model from a file.

        Args:
            filepath (str): Path to the saved model file.

        Returns:
            NHLMarkovModel: Loaded model instance.
        """
        model = cls()
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            model.transitions = data['transitions']
            model.is_normalized = data['is_normalized']
            model.states = data['states']
        return model