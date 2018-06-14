from datetime import datetime

class AgentState:
    """
    Class representing the agent's state at any given moment.
    """

    actions = ['request_ally', 'request_grid', 'grant', 'deny_request', 'consume_and_store']

    def __init__(self, name, energy_consumption, energy_generation, battery_curr, time, environment_state,
                 cg_http_service):
        print("registering state...")
        self.name = name
        self.energy_consumption = energy_consumption
        self.energy_generation = energy_generation
        self.battery_max = 5.76
        self.battery_curr = battery_curr
        self.time = time

        self.environment_state = environment_state
        self.cg_http_service = cg_http_service


    def get_possible_actions(self, actions = None):
        '''
        Computes the set of all legal actions allowed in this state
        :return: array of legal actions
        '''
        possible_actions = []

        if actions is None:

            if(self.energy_generation + self.battery_curr > self.energy_consumption):
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


    def get_score(self):
        score = 0.0
        # if it is in the positive state
        # if (self.energy_generation + self.battery_curr) >= self.energy_consumption:
        #     score += 1
        # elif (self.energy_generation + self.battery_curr) < self.energy_consumption:
        #     score -= 10
        #
        # if there is remaining charge in the battery
        if self.battery_curr > 0.0:
            score += 1.0

        # overall impact of the agent on the environment
        if (self.environment_state.get_total_generated() + self.environment_state.get_energy_borrowed_from_ally()) \
                >= (self.environment_state.get_total_consumed() + self.environment_state.get_energy_borrowed_from_CG()):
            score += 1.0
        elif (self.environment_state.get_total_generated() + self.environment_state.get_energy_borrowed_from_ally()) \
                < (self.environment_state.get_total_consumed() + self.environment_state.get_energy_borrowed_from_CG()):
            score -= 1.0


        # Add global state information
        #community_status = self.cg_http_service.get_energy_status()


        return score


    def reset(self, battery_init):
        self.energy_consumption = 0.0
        self.energy_generation = 0.0
        self.battery_curr = battery_init
        self.time =  datetime.strptime('2014/01/01 12:00', '%Y/%m/%d %H:%M')
        self.environment_state = EnvironmentState(0.0, 0.0, 0.0, 0.0)


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

    def update_total_consumed(self, energy):
        self.total_consumed = self.total_consumed + energy

    def get_total_generated(self):
        return self.total_generated

    def set_total_generated(self, energy):
        self.total_generated = energy

    def update_total_generated(self, energy):
        self.total_generated = self.total_generated + energy

    def get_energy_borrowed_from_CG(self):
        return self.central_grid

    def update_energy_borrowed_from_CG(self, energy):
        self.central_grid = self.central_grid + energy

    def get_energy_borrowed_from_ally(self):
        return self.energy_borrowed_from_ally

    def update_energy_borrowed_from_ally(self, energy):
        self.energy_borrowed_from_ally = self.energy_borrowed_from_ally + energy

    def __str__(self):
        str_rep = """
        Total Generated: {0}
        Total Consumed: {1}
        Total Borrowed From CG: {2}
        Total Borrowed From Allies: {3}
        """.format(self.total_generated, self.total_consumed, self.central_grid, self.energy_borrowed_from_ally)

        return str_rep
