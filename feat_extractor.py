import util
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from state import AgentState

class FeatureExtractor:

    def __init__(self):
        print("Instantiating feature extractor...")
        self._train()


    def _train(self):

        # self.ohe_hour = OneHotEncoder(sparse=False)
        # self.ohe_hour.fit(np.array(range(0,48)))
        #
        # self.ohe_month = OneHotEncoder(sparse=False)
        # self.ohe_month.fit(np.array(range(0, 12)))
        #
        # self.ohe_day = OneHotEncoder(sparse=False)
        # self.ohe_day.fit(np.array(range(0, 31)))

        train_x = np.zeros(shape=[365 * 48, 3])

        for i in range (0, (365 * 48)):
            train_x[i][0] = i%48

        for i in range (0, (365 * 48)):
            train_x[i][1] = i%7

        for i in range (0, (365 * 48)):
            train_x[i][2] = i%12

        self.ohe_time = OneHotEncoder(sparse=False)
        self.ohe_time.fit(train_x)

        self.lb_actions = LabelEncoder()
        actions_trans = self.lb_actions.fit_transform(AgentState.actions)
        self.ohe_actions = OneHotEncoder(sparse=False)
        self.ohe_actions.fit(actions_trans.reshape(-1,1))

    def get_features(self, state, action):
        '''
        Compute the features from the state to extract the q-value
        :param state:
        :param action:
        :return: a list of feature values
        '''

        time_feat = util.Counter()
        time_feat['hour'] = (state.time.time().hour * 60 + state.time.time().minute) // 30
        time_feat['dayofweek'] = state.time.weekday() # monday = 0
        time_feat['month'] = state.time.month - 1

        # Transform and avoid the dummy variable trap
        features = self.ohe_time.transform(np.array([time_feat['hour'], time_feat['dayofweek'], time_feat['month']])
                                           .reshape(1, -1))[:, :-1]

        features = list(features[0])

        features.append(state.energy_consumption)
        features.append(state.energy_generation)
        features.append(state.battery_curr)


        # TODO Embed action as a feature into this
        # Modelling energy request data
        if action['action'] == 'grant' or action['action'] == 'deny_request':
            features.append(action['data'])
        else:
            features.append(0)

        action_trans = self.ohe_actions.transform(self.lb_actions.transform([action['action']]).reshape(1,-1))
        for f in action_trans[0]:
            features.append(f)


        # Transforming into apt data structure
        feat_dict = util.Counter()
        for i in range(len(features)):
            feat_dict['f_'+str(i)] = float(features[i])

        return feat_dict
