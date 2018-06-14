import state
import util
import random
import torch
import copy
import torch.autograd as autograd
import torch.nn as nn
from collections import namedtuple
from marlagent.dqn.model import DQN
from marlagent.dqn.replay_buffer import ReplayBuffer
from feat_extractor import FeatureExtractor

USE_CUDA = torch.cuda.is_available()
dtype = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor

class Variable(autograd.Variable):
    def __init__(self, data, *args, **kwargs):
        if USE_CUDA:
            data = data.cuda()
        super(Variable, self).__init__(data, *args, **kwargs)


OptimizerSpec = namedtuple("OptimizerSpec", ["constructor", "kwargs"])

Statistic = {
    "mean_episode_rewards": [],
    "best_mean_episode_rewards": []
}



class LearningAgent():

    def __init__(self,
                 n_features,
                 batch_size,
                 optimizer_spec,
                 gamma = 0.99,
                 target_update_freq = 100):

        n_actions = len(state.AgentState.actions)
        curr_batch_size = 0
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        self.num_param_updates = 0
        self.curr_batch_size = 0

        self.feat_extractor = FeatureExtractor()

        # two different networks
        self.Q = DQN(n_features, n_actions)
        self.target_Q = DQN(n_features, n_actions)

        self.replay_buffer = ReplayBuffer(buffer_size=100, n_features=n_features)

        # Construct Q network optimizer function
        self.optimizer = optimizer_spec.constructor(self.Q.parameters(), **optimizer_spec.kwargs)



    def get_action(self, state, actions = None):
        """
        Compute the action to take in the current state.
        Epsilon decides whether to exploit the current policy or choice a new action randomly.

        A small value for epsilon indicates lesser exploration.
        :param state:
        :return: appropriate action to take in the current state
        """
        legal_actions = self._get_legal_actions(state, actions)
        action = None

        if util.flip_coin(self.epsilon):
            print("Randomizing action...")
            action = random.choice(legal_actions)
        else:
            print("Selecting the best action based on policy...")
            action = self.select_action_from_policy(state, actions)

        # Book keeping
        self.recent_observation = state
        self.recent_action = action

        return action


    def select_action_from_policy(self, state, actions):
        """

        :param state:
        :param actions: set of legal actions allowed in this state
        :return:
        """
        actions = self._get_legal_actions(state, actions)

        if len(actions) == 0:
            print("Something wrong. Check!. Maybe all actions are done.")
            return None

        state_feat = self.feat_extractor.encode_state(state)

        idx, state_arr = self.replay_buffer.store_state(state_features=state_feat)
        state_ts = torch.from_numpy(state_arr).type(dtype).unsqueeze(0)

        # TODO: Check What is format of the actions being returned. Will use a Softmax function
        q_values_ts = self.Q(Variable(state_ts, volatile=True)).data
        output_actions = q_values_ts.max(1)[1].cpu()

        # filter action from the list of actions returned as a softmax function
        action = self.filter_actions(actions, output_actions)

        return action


    def update(self, state, action, next_state, reward):

        # Sampling a batch of transitions from the replay buffer
        obs_batch, act_batch, rew_batch, next_obs_batch = self.replay_buffer.sample(self.batch_size)

        # Convert numpy nd_array to torch variables for calculation
        obs_batch = Variable(torch.from_numpy(obs_batch).type(dtype))
        act_batch = Variable(torch.from_numpy(act_batch).long())
        rew_batch = Variable(torch.from_numpy(rew_batch))
        next_obs_batch = Variable(torch.from_numpy(next_obs_batch).type(dtype))

        if USE_CUDA:
            act_batch = act_batch.cuda()
            rew_batch = rew_batch.cuda()

        # Compute current Q value, q_func takes only state and output value for every state-action pair
        # We choose Q based on action taken.
        current_Q_values = self.Q(obs_batch).gather(1, act_batch.unsqueeze(1))

        # Compute next Q value based on which action gives max Q values
        # Detach variable from the current graph since we don't want gradients for next Q to propagated
        next_max_q = self.target_Q(next_obs_batch).detach().max(1)[0]

        # Compute the target of the current Q values
        target_Q_values = rew_batch + (self.gamma * next_max_q)

        # Compute Bellman error
        bellman_error = target_Q_values - current_Q_values

        # clip the bellman error between [-1 , 1]
        clipped_bellman_error = bellman_error.clamp(-1, 1)

        d_error = clipped_bellman_error * -1.0

        # Clear previous gradients before backward pass
        self.optimizer.zero_grad()

        # run backward pass
        current_Q_values.backward(d_error.data.unsqueeze(1))

        # Perfom the update
        self.optimizer.step()
        self.num_param_updates += 1

        # Periodically update the target network by Q network to target Q network
        if self.num_param_updates % self.target_update_freq == 0:
            self.target_Q.load_state_dict(self.Q.state_dict())


    def _get_legal_actions(self, agent_state, actions=None):
        """
        Computes the set of actions a agent should take from the set of possible actions
        :param agent_state:
        :param actions:
        :return: legal actions the agent can take
        """
        possible_actions = agent_state.get_possible_actions(actions)

        # TODO some filtering of actions

        legal_actions = copy.deepcopy(possible_actions)

        return legal_actions


    def filter_actions(self, legal_actions, actions):

        action_reward = 0.0
        # if action with highest probability is not in legal actions


