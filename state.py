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
        self.battery_max = 8.0
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
        score = 0.0
        # if it is in the positive state
        if (self.energy_generation + self.battery_curr) >= self.energy_consumption:
            score += 10
        elif (self.energy_generation + self.battery_curr) < self.energy_consumption:
            score -= 10

        # if there is remaining charge in the battery
        if self.battery_curr > 0:
            score += 10

        # overall impact of the agent on the environment
        if (self.environment_state.get_total_generated() + self.environment_state.get_energy_borrowed_from_ally()) \
                >= (self.environment_state.get_total_consumed() + self.environment_state.get_energy_borrowed_from_CG()):
            score += 10
        elif (self.environment_state.get_total_generated() + self.environment_state.get_energy_borrowed_from_ally()) \
                < (self.environment_state.get_total_consumed() + self.environment_state.get_energy_borrowed_from_CG()):
            score -= 10

        return score


    def __str__(self):
        str_rep = """
        Time: {0}
        Energy Generation: {1}
        Energy Consumption {2}
        Battery Current: {3}
        Battery Max: {4}
        """.format(self.time, self.energy_generation, self.energy_consumption, self.battery_curr, self.battery_max)

        return str_rep


class EnvironmentState:
    """
    Maintains the state of the environment
    """

    def __init__(self, total_consumed, total_generated, central_grid, energy_borrowed_from_ally):
        self.total_consumed = total_consumed
        self.total_generated = total_generated
        self.central_grid = central_grid
        self.energy_borrowed_from_ally = energy_borrowed_from_ally

    def get_total_consumed(self):
        return self.total_consumed

    def set_total_consumed(self, energy):
        self.total_consumed = self.total_consumed + energy

    def get_total_generated(self):
        return self.total_generated

    def set_total_generated(self, energy):
        self.total_generated = self.total_generated + energy

    def get_energy_borrowed_from_CG(self):
        return self.central_grid

    def set_energy_borrowed_from_CG(self, energy):
        self.central_grid = self.central_grid + energy

    def get_energy_borrowed_from_ally(self):
        return self.energy_borrowed_from_ally

    def set_energy_borrowed_from_ally(self, energy):
        self.energy_borrowed_from_ally = self.energy_borrowed_from_ally + energy

    def __str__(self):
        str_rep = """
        Total Generated: {0}
        Total Consumed: {1}
        Total Borrowed From CG: {2}
        Total Borrowed From Allies: {3}
        """.format(self.total_generated, self.total_consumed, self.central_grid, self.energy_borrowed_from_ally)

        return str_rep
