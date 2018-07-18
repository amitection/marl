from collections import namedtuple

import numpy as np
import torch
import torch.autograd as autograd
import torch.optim as optim

from marlagent import rlagent
from marlagent.agent.dqn.model import DQN
from marlagent.agent.dqn.replay_buffer import ReplayBuffer

USE_CUDA = torch.cuda.is_available()
dtype = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor


class Variable(autograd.Variable):
    def __init__(self, data, *args, **kwargs):
        if USE_CUDA:
            data = data.cuda()
        super(Variable, self).__init__(data, *args, **kwargs)


OptimizerSpec = namedtuple("OptimizerSpec", ["constructor", "kwargs"])

optimizer_spec = OptimizerSpec(
        constructor=optim.RMSprop,
        kwargs=dict(lr=0.00025, alpha=0.95, eps=0.01),
    )


class DQNAgent(rlagent.RLAgent):

    def __init__(self):

        super(DQNAgent, self).__init__()
        print("DQN initiated...")

        self.learning_freq = 10
        self.learning_starts = 1000
        self.target_update_freq = 50
        self.num_updates = 0
        self.num_calls = 0
        self.discount = 0.99

        self.n_features = self.feat_extractor.get_n_features()

        # Instantiating a MLP model
        self.Q = DQN(self.n_features)
        self.target_Q = DQN(self.n_features)

        self.replay_buffer = ReplayBuffer(size = 10000, n_features = self.n_features)


        # Construct Q network optimizer function
        self.optimizer = optimizer_spec.constructor(self.Q.parameters(), **optimizer_spec.kwargs)



    def get_qValue(self, state, action):

        features = self.feat_extractor.get_features(state, action)
        feat_arr = self.__transform_to_numpy(features)

        state_ts = torch.from_numpy(feat_arr).type(dtype).unsqueeze(0)
        q_values_ts = self.Q(Variable(state_ts, volatile=True)).data

        print("Calculated Q-Value for action ({0}): {1}".format(action['action'], q_values_ts))

        # Use volatile = True if variable is only used in inference mode, i.e. don’t save the history
        return q_values_ts



    def update(self, state, action, next_state, reward, eoi = False):

        if eoi == True:
            self.replay_buffer.update_last_transition_with_reward(reward)
        else:
            features = self.feat_extractor.get_features(state, action)

            # store the converted state in the replay buffer
            # if action['action'] != 'consume_and_store':
            self.num_calls += 1
            self.replay_buffer.store_transition(features, action, reward)

            # Perform the update in a batch. Apply the average error over all fields

        if self.num_calls > self.learning_starts and self.num_calls % self.learning_freq == 0:
            self.perform_update(state.name, reward = 0)


    def perform_update(self, agent_name, reward):

        #TODO: Ignore reward from EOI handler

        print("Updating network...")
        obs, next_obs, r, eoi = self.replay_buffer.sample(batch_size=64)

        #reward = reward * np.zeros(obs.shape[0])
        # r[r.shape[0] - 1] = reward
        reward = r

        obs_batch = Variable(torch.from_numpy(obs).type(dtype))
        reward_batch = Variable(torch.from_numpy(reward).type(dtype))
        next_obs_batch = Variable(torch.from_numpy(next_obs).type(dtype))
        not_eoi = Variable(torch.from_numpy(1 - eoi)).type(dtype)

        current_Q_values = self.Q(obs_batch)
        target_Q_values = self.target_Q(next_obs_batch).detach()
        target_Q_values = target_Q_values * not_eoi

        # print("CURR Q VALUE:", current_Q_values)
        # print("TARGET Q VALUE:", target_Q_values)
        # print("REWARD BATCH", reward_batch)
        print("Not EOI", not_eoi)


        q_value_curr_state = current_Q_values
        q_value_next_state = reward_batch + (self.discount * target_Q_values)
        # print("Q VALUE NEXT STATE:", q_value_next_state)

        # Compute Bellman error
        bellman_error = q_value_next_state - q_value_curr_state
        # print("BELLMAN ERROR:", bellman_error)

        # clip the bellman error between [-1 , 1]
        clipped_bellman_error = bellman_error.clamp(-1, 1)
        # print("Bellman Error:", clipped_bellman_error)

        d_error = clipped_bellman_error * -1.0
        # print("Delta Error:", d_error.data.unsqueeze(1))
        print("Delta Error:", d_error.data.mean())

        self.write_to_file(data=d_error.mean(), path_to_file='assets/' + agent_name + 'error.csv')

        # Clear previous gradients before backward pass
        self.optimizer.zero_grad()

        new_q_value_curr_state = Variable(q_value_curr_state.data, requires_grad=True)
        # new_q_value_curr_state.backward()
        new_q_value_curr_state.backward(d_error.data)

        # Perfom the update
        self.optimizer.step()

        # Clear stored values in the replay buffer
        # self.replay_buffer.reset()
        print("Updating network finished.")

        self.num_updates += 1

        # Periodically update the target network with the Q network
        if self.num_updates % self.target_update_freq == 0:
            self.target_Q.load_state_dict(self.Q.state_dict())
            print("Updating target Q network finished.")


    def __transform_to_numpy(self, features):
        numpy_arr = np.array(features, dtype=np.float32)
        return numpy_arr
