import util
import numpy as np
from state import EnvironmentState
from datetime import datetime
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from state import AgentState

class FeatureExtractor:

    def __init__(self):
        print("Instantiating feature extractor...")
        self._train()


    def _train(self):

        train_x = np.zeros(shape=[365 * 48, 2])

        for i in range (0, (365 * 48)):
            train_x[i][0] = i%48

        for i in range (0, (365 * 48)):
            train_x[i][1] = i%7

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

        features = self.encode_state(state)

        # ---------------- ENCODING ACTIONS ----------------
        # Modelling energy request data
        if action['action'] == 'grant' or action['action'] == 'deny_request':
            # TODO: Discritize by observing the values of data
            features.append(int(action['data']/0.2))

        else:
            features.append(0)

        action_trans = self.ohe_actions.transform(self.lb_actions.transform([action['action']]).reshape(1,-1))
        for f in action_trans[0]:
            features.append(f)

        return features


    def encode_state(self, state):
        '''
        Encode the state variable into n features
        :param state:
        :return:
        '''

        time_feat = util.Counter()
        time_feat['hour'] = (state.time.time().hour * 60 + state.time.time().minute) // 30
        time_feat['dayofweek'] = state.time.weekday()  # monday = 0
        # time_feat['month'] = state.time.month - 1

        # Transform and avoid the dummy variable trap
        features = self.ohe_time.transform(np.array([time_feat['hour'], time_feat['dayofweek']])
                                           .reshape(1, -1))[:, :-1]

        features = list(features[0])

        features.append(self.__encode_energy(state.energy_consumption))
        features.append(self.__encode_energy(state.energy_generation))
        features.append(self.__encode_energy(state.battery_curr))

        return features


    def __encode_features_to_Counter(self, features):
        # Transforming into apt data structure
        feat_dict = util.Counter()
        for i in range(len(features)):
            feat_dict['f_' + str(i)] = float(features[i])

        # print(feat_dict)
        return feat_dict


    def get_n_features(self):
        '''
        Simulates a fake agent state and returns the numbers of features.
        :param state:
        :return:
        '''

        environment_state = EnvironmentState(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        fake_agent_state = AgentState(name='Test', iter =0, energy_consumption=0.0, energy_generation=0.0,
                                      battery_curr=float(5), time=datetime.now(),
                                      environment_state=environment_state,
                                      cg_http_service=None)
        action = {}
        action['action'] = 'consume_and_store'
        features = self.get_features(fake_agent_state, action)

        return len(features)


    def __encode_energy(self, energy):
        if energy == 0.0:
            return 0
        elif energy < 1.0:
            return 1.0
        elif energy < 2.88:
            return 2.0
        else:
            return 3


