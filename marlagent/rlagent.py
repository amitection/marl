import util
import random
import feat_extractor as fe

class RLAgent:

    def __init__(self, alpha=1.0, epsilon=0.05, gamma=0.8, numTraining = 10):

        print("RL agent instantiated...")
        self.alpha = float(alpha) # learning rate
        self.epsilon = float(epsilon) # exploration vs exploitation
        self.discount = float(gamma) # significance of future rewards
        self.numTraining = int(numTraining)

        self.weights = util.Counter()

        self.feat_extractor = fe.FeatureExtractor()


    def get_qValue(self, state, action):
        """
        Should return Q(state,action) = w * featureVector
        where * is the dotProduct operator

        :param state:
        :param action:
        :return:
        """

        # TODO
        features = self.feat_extractor.get_features(state, action)

        q_value = 0.0
        for f_key in features:
            q_value = q_value + (features[f_key] * self.weights[f_key])

        return q_value


    def compute_action_from_qValues(self, state):
        """
        Iterate over all the actions and compute their q-values. Then return the action with the highest q-value.

        :param state:
        :return:
        """
        actions = self._get_legal_actions(state)

        if len(actions) == 0:
            print("Something wrong. Check!. Maybe all actions are done.")
            return None

        # Populating a new list of (action, value) pair from list of q_values
        action_value_pair = []
        for action in actions:
            action_value_pair.append((action, self.get_qValue(state, action)))

        # Returning the action with maximum q_value
        return max(action_value_pair, key=lambda x: x[1])[0]


    def get_action(self, state):
        """
        Compute the action to take in the current state.
        Epsilon decides whether to exploit the current policy or choice a new action randomly.

        A small value for epsilon indicates lesser exploration.
        :param state:
        :return: appropriate action to take in the current state
        """
        legal_actions = self._get_legal_actions(state)
        action = None

        if util.flip_coin(self.epsilon):
            action = random.choice(legal_actions)
        else:
            action = self.get_policy(state)

        return action


    def update(self, state, action, next_state, reward):
        """
        Update weights based on transition

        :param state:
        :param action:
        :param nextState:
        :param reward:
        :return:
        """
        # TODO
        features = self.feat_extractor.get_features(state, action)
        difference = reward + (self.discount * self.get_value(next_state)) - self.get_qValue(state, action)

        for f_key in features:
            self.weights[f_key] = self.weights[f_key] + (self.alpha * difference * features[f_key])

        # Write weights into a file to observe learning
        print(self.weights)


    def get_policy(self, state):
        return self.compute_action_from_qValues(state)


    def do_action(self, state, action):
        util.raiseNotDefined()


    def get_weights(self):
        return self.weights


    def _get_legal_actions(self, agent_state):
        """
        Computes the set of actions a agent should take from the set of possible actions
        :param agent_state:
        :return: legal actions the agent can take
        """
        legal_actions =[]
        possible_actions = agent_state.get_possible_actions()

        if 'consume_and_store' in possible_actions and 'grant' in possible_actions:
            legal_actions.append('consume_and_store')

        return legal_actions
