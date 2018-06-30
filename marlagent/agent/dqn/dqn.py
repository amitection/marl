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

        self.learning_freq = 48

        self.n_features = self.feat_extractor.get_n_features()

        # Instantiating a MLP model
        self.Q = DQN(self.n_features)

        self.replay_buffer = ReplayBuffer(size = 48, n_features = self.n_features)


        # Construct Q network optimizer function
        self.optimizer = optimizer_spec.constructor(self.Q.parameters(), **optimizer_spec.kwargs)



    def get_qValue(self, state, action):

        print("Calling Q VALUE method of DQN")

        features = self.feat_extractor.get_features(state, action)
        feat_arr = self.__transform_to_numpy(features)

        state_ts = torch.from_numpy(feat_arr).type(dtype).unsqueeze(0)
        q_values_ts = self.Q(Variable(state_ts, volatile=True)).data

        print("Calculated Q-Value: ",q_values_ts)

        # Use volatile = True if variable is only used in inference mode, i.e. don’t save the history
        return q_values_ts



    def update(self, state, action, next_state, reward):

        features = self.feat_extractor.get_features(state, action)

        # store the converted state in the replay buffer
        self.replay_buffer.store_transition(features, action, reward)

        # extract the current index of the replay buffer
        # sub by -1 as the index is incremented after each insertion
        curr_idx = self.replay_buffer.idx - 1

        # Perform the update in a batch. Apply the average error over all fields
        if(curr_idx % self.learning_freq == 0):

            obs, next_obs, reward = self.replay_buffer.sample(batch_size=48)

            obs_batch = Variable(torch.from_numpy(obs).type(dtype))
            reward_batch = Variable(torch.from_numpy(reward))
            next_obs_batch = Variable(torch.from_numpy(next_obs).type(dtype))

            current_Q_values = self.Q(obs_batch)
            target_Q_values = self.Q(next_obs_batch).detach()

            q_value_curr_state = current_Q_values
            q_value_next_state = reward_batch + (self.discount * target_Q_values)

            # Compute Bellman error
            bellman_error = reward + q_value_next_state - q_value_curr_state

            # clip the bellman error between [-1 , 1]
            clipped_bellman_error = bellman_error.clamp(-1, 1)
            print("Bellman Error:", clipped_bellman_error)

            d_error = clipped_bellman_error * -1.0
            print("Delta Error:",d_error)

            self.write_to_file(data=d_error, path_to_file='assets/' + state.name + 'error.csv')

            # Clear previous gradients before backward pass
            self.optimizer.zero_grad()

            new_q_value_curr_state = Variable(q_value_curr_state.data, requires_grad=True)
            # new_q_value_curr_state.backward()
            # new_q_value_curr_state.backward(d_error.data.unsqueeze(1))
            new_q_value_curr_state.backward(d_error.data.unsqueeze(1))

            # Perfom the update
            self.optimizer.step()

            # Clear stored values in the replay buffer
            self.replay_buffer.reset()

    def __transform_to_numpy(self, features):
        numpy_arr = np.array(features, dtype=np.float32)
        return numpy_arr
