from collections import namedtuple

import numpy as np
import torch
import torch.autograd as autograd
import torch.optim as optim

from feat_extractor import FeatureExtractor
from marlagent import rlagent
from marlagent.agent.dqn.model import DQN

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

    def __init__(self, n_features=69):

        super(DQNAgent, self).__init__()
        print("DQN initiated...")

        self.num_param_updates = 0
        self.curr_batch_size = 0

        self.n_features = self.feat_extractor.get_n_features()

        # Instantiating a MLP model
        self.Q = DQN(self.n_features)


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
        feat_arr = self.__transform_to_numpy(features)

        q_value_next_state = (self.discount * self.compute_value_from_qValues(next_state))
        q_value_curr_state = self.get_qValue(state, action)

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
        new_q_value_curr_state.backward()
        # q_value_curr_state.backward(d_error.data.unsqueeze(1))

        # Perfom the update
        self.optimizer.step()


    def __transform_to_numpy(self, features):
        numpy_arr = np.array(features, dtype=np.float32)
        return numpy_arr
