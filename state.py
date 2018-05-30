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

    actions = ['request', 'grant', 'deny_request', 'consume_and_store']

    def __init__(self, name, energy_consumption, energy_generation, battery_curr, time):
        print("registering state...")
        self.name = name
        self.energy_consumption = energy_consumption
        self.energy_generation = energy_generation
        self.battery_max = 280
        self.battery_curr = battery_curr
        self.time = time

    def get_possible_actions(self):
        '''
        Computes the set of all legal actions allowed in this state
        :return: array of legal actions
        '''
        possible_actions = []

        if(self.energy_generation > self.energy_consumption):
            possible_actions.append('consume_and_store')
            possible_actions.append('grant')
        else:
            possible_actions.append('request')

        return possible_actions


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