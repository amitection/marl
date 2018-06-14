import numpy as np
import feat_extractor

class ReplayBuffer:

    def __init__(self, buffer_size, n_features):
        """
        https://github.com/transedward/pytorch-dqn/blob/master/utils/replay_buffer.py
        https://datascience.stackexchange.com/questions/20535/understanding-experience-replay-in-reinforcement-learning

        This replay buffer stores n past states and next states along with the rewards.
        """

        self.size = buffer_size
        self.n_features = n_features
        self.next_idx = 0

        self.states = None
        self.actions = None
        self.rewards = None
        self.done = None


    def store_transition(self, state, action, reward):
        """

        :param state: the state included everything in my case. even the action
        :param action:
        :param reward:
        :return:
        """
        if self.states is None:
            self.states = np.empty(([self.size], self.n_features), dtype=np.float32)
            self.actions = np.empty([self.size], dtype=np.int32)
            self.rewards = np.empty([self.size], dtype=np.float32)
            self.done = np.empty([self.size], dtype=np.bool)

        self.states = np.append(arr=self.states, values = [state], axis = 0)
        self.rewards = np.append(arr=self.rewards, values=[reward], axis = 0)