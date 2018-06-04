import copy

class AgentState:
    """
    Energy Consumption
    Energy Generation
    Energy consumption at t+1
    Energy generation at t+1
    Current storage (Scurr)
    Smax - Scurr
    Amount of Requested Energy
    Hour of the day - 48
    Day of the week
    Month of the year
    """

    actions = ['request_ally', 'request_grid', 'grant', 'deny_request', 'consume_and_store']

    def __init__(self, name, energy_consumption, energy_generation, battery_curr, time, environment_state):
        print("registering state...")
        self.name = name
        self.energy_consumption = energy_consumption
        self.energy_generation = energy_generation
        self.battery_max = 280
        self.battery_curr = battery_curr
        self.time = time

        self.environment_state = environment_state


    def get_possible_actions(self, actions = None):
        '''
        Computes the set of all legal actions allowed in this state
        :return: array of legal actions
        '''
        possible_actions = []

        if actions is None:

            if(self.energy_generation > self.energy_consumption):
                possible_actions.append({'action':'consume_and_store', 'data':None})
            else:
                possible_actions.append({'action':'request_ally', 'data':None})
                possible_actions.append({'action':'request_grid', 'data':None})

        else:
            # Case when only options are grant or deny
            # Simply deny the request if current battery is 0
            if self.battery_curr <= 0:
                for action in actions:
                    if action['action'] == 'deny_request':
                        possible_actions.append(action)
            else:
                possible_actions = actions

        return possible_actions


    def get_successor_state(self, action):
        """
        Observe the state transition on the input action and return the next state.

        :param state:
        :param action:
        :return: next state
        """
        #TODO


        return self


    def get_score(self):
        #TODO
        return "the score of this current state"


class EnvironmentState:
    """
    Maintains the state of the environment
    """

    def __init__(self, total_consumed, total_generated):
        self.total_consumed = total_consumed
        self.total_generated = total_generated

    def get_total_consumed(self):
        return self.total_consumed

    def get_total_generated(self):
        return self.total_generated