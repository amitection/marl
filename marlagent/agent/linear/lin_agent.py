import util

from marlagent import rlagent

class LinearQAgent(rlagent.RLAgent):

    def __init__(self):

        print("Linear Approximate Q learning agent instantiated...")
        super(LinearQAgent, self).__init__()

        self.weights = util.Counter()


    def get_qValue(self, state, action):
        """
        Should return Q(state,action) = w * featureVector
        where * is the dotProduct operator

        :param state:
        :param action:
        :return:
        """
        features = self.feat_extractor.get_features(state, action)

        q_value = 0.0
        for f_key in features:
            q_value = q_value + (features[f_key] * self.weights[f_key])

        # print(features)
        # print("Q - VALUE:::::%s"%q_value)
        return q_value


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
        # difference = reward + (self.discount * self.compute_value_from_qValues(next_state)) - self.get_qValue(state, action)
        q_value_next_state = (self.discount * self.compute_value_from_qValues(next_state))
        q_value_curr_state = self.get_qValue(state, action)
        d_error = reward + q_value_next_state - q_value_curr_state

        # print("DISCOUNTED Q VALUE NEXT STATE:%s"%q_value_next_state)
        # print("Q VALUE CURR STATE:%s" % q_value_curr_state)
        print("CORRECTION-------------:%s"%d_error)
        self.write_to_file(data = d_error, path_to_file = 'assets/'+state.name+'error.csv')

        for f_key in features:
            self.weights[f_key] = self.weights[f_key] + (self.alpha * d_error * features[f_key])

        # Write weights into a file to observe learning
        # print("WEIGHTS---------------:")
        # print(self.weights)



    def get_weights(self):
        return self.weights