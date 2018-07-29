import os
import util
import random
import copy
import feat_extractor as fe
from marlagent import agent_actions

class RLAgent:

    def __init__(self, alpha=0.001, epsilon=1.0, gamma=0.9, numTraining = 10):

        print("RL agent instantiated...")
        self.alpha = float(alpha) # learning rate
        self.epsilon = float(epsilon) # exploration vs exploitation
        self.discount = float(gamma) # significance of future rewards
        self.numTraining = int(numTraining)

        self.feat_extractor = fe.FeatureExtractor()
        self.central_grid = util.Counter() # note the energy borrowed from central grid



    def get_qValue(self, state, action):
        pass



    def update(self, state, action, next_state, reward, update = False):
        pass



    def compute_value_from_qValues(self, state):
        """
        Compute the q_value for each action and return the max Q-value as the value of that state

        :param state:
        :return:
        """

        # No actions available
        if len(self._get_legal_actions(state)) == 0:
            return 0.0

        q_values_for_this_state = []
        for action in self._get_legal_actions(state):
            q_values_for_this_state.append(self.get_qValue(state, action))

        return max(q_values_for_this_state)



    def compute_action_from_qValues(self, state, actions = None):
        """
        Iterate over all the actions and compute their q-values. Then return the action with the highest q-value.

        :param state:
        :return:
        """
        actions = self._get_legal_actions(state, actions)

        if len(actions) == 0:
            print("Something wrong. Check!. Maybe all actions are done.")
            return None

        # Populating a new list of (action, value) pair from list of q_values
        action_value_pair = []
        for action in actions:
            action_value_pair.append((action, self.get_qValue(state, action)))

        # Returning the action with maximum q_value
        #TODO: if q values for multiple action value pairs is the same it picks the first one. Need to randomize this selection
        return max(action_value_pair, key=lambda x: x[1])[0]



    def get_action(self, state, actions = None):
        """
        Compute the action to take in the current state.
        Epsilon decides whether to exploit the current policy or choice a new action randomly.

        A small value for epsilon indicates lesser exploration.
        :param state:
        :return: appropriate action to take in the current state
        """
        legal_actions = self._get_legal_actions(state, actions)
        action = None

        if util.flip_coin(self.epsilon):
            print("Randomizing action...")
            action = random.choice(legal_actions)
        else:
            print("Selecting the best action based on policy...")
            action = self.get_policy(state, actions)

        return action



    def get_policy(self, state, actions):
        return self.compute_action_from_qValues(state, actions)



    def do_action(self, state, action, ns, agent, agent_name, allies):
        '''
        Perform an action and return the next state
        :param state:
        :param action:
        :return: the next state on taking the action
        '''
        next_state = copy.deepcopy(state)
        next_state.environment_state.update_total_consumed(state.energy_consumption)
        next_state.environment_state.update_total_generated(state.energy_generation)

        usable_generated_energy =  state.energy_generation

        time_str = util.cnv_datetime_to_str(state.time, '%Y/%m/%d %H:%M')
        if action['action'] == 'consume_and_store':

            diff = state.energy_generation - state.energy_consumption

            # Store the unused energy and return the excess
            batt_curr, excess = agent_actions.update_battery_status(state.battery_max, state.battery_curr, diff)

            # Subtract the energy which could not be used
            usable_generated_energy = usable_generated_energy - excess
            next_state.environment_state.set_total_generated(next_state.environment_state.get_total_generated() - excess)

            next_state.battery_curr = batt_curr
            next_state.energy_generation = 0.0
            next_state.energy_consumption = 0.0


        if action['action'] == 'request_ally':
            # TODO think about what to do if ally does not serve request
            diff = (state.energy_generation + state.battery_curr) - state.energy_consumption
            agent.log_info("---------Energy Diff: "+str(diff))
            energy_grant = 0.0
            if diff < 0.0:
                energy_grant = agent_actions.request_ally(ns=ns, agent=agent, agent_name = agent_name, allies=allies, energy_amt = abs(diff), time = time_str)
                # energy_grant = abs(diff)
                next_state.energy_generation = 0.0
                next_state.battery_curr = 0.0
                next_state.environment_state.update_energy_borrowed_from_ally(energy_grant)

                # TODO think how to handle energy consumption if
                # If energy consumption is positive in next state then penalize agent
                next_state.energy_consumption = abs(diff) - energy_grant

                if next_state.energy_consumption > 0:
                    self.central_grid[time_str] = next_state.energy_consumption
                    next_state.environment_state.update_energy_borrowed_from_CG(self.central_grid[time_str])
                    #next_state.energy_consumption = 0.0

            else:
                print("Ally not requested as enough energy available in battery.")
                next_state.energy_generation = 0.0
                next_state.energy_consumption = 0.0
                next_state.battery_curr = diff


        if action['action'] == 'request_grid':
            # calculate the energy difference
            energy_diff = abs(agent_actions.get_energy_balance(state))
            self.central_grid[time_str] = energy_diff

            next_state.energy_consumption = 0.0
            next_state.energy_generation = 0.0
            next_state.battery_curr = 0.0
            next_state.environment_state.update_energy_borrowed_from_CG(energy_diff)


        if action['action'] == 'grant':
            energy_request = action['data']
            bal = (state.energy_generation + state.battery_curr) - energy_request
            energy_grant = 0.0

            if(bal >= 0):
                energy_grant = energy_request
                next_state.energy_generation = 0.0
                next_state.battery_curr, excess = agent_actions.update_battery_status(state.battery_max, state.battery_curr,
                                                                              -energy_grant)
                agent.log_info("Granting full energy.")

            elif(bal < 0):
                energy_grant = (state.energy_generation + state.battery_curr)
                next_state.energy_generation = 0.0
                next_state.battery_curr = 0.0
                agent.log_info("Granting partial energy.")

            # A more complex case can be designed where it gives partial energy

            return (next_state, energy_grant)

        if action['action'] == 'deny_request':
            energy_grant = 0.0
            return (next_state, energy_grant)

        return (next_state, usable_generated_energy)


    def write_to_file(self, data, path_to_file = 'assets/error.csv'):

        if os.path.isfile(path_to_file):
            with open(path_to_file, mode='a') as f:
                f.write(str(data)+str("\n"))
                f.close()

        else:
            with open(path_to_file, 'w+') as f:
                f.write(str(data)+str("\n"))
                f.close()



    def _get_legal_actions(self, agent_state, actions=None):
        """
        Computes the set of actions a agent should take from the set of possible actions
        :param agent_state:
        :param actions:
        :return: legal actions the agent can take
        """
        possible_actions = agent_state.get_possible_actions(actions)

        # TODO some filtering of actions

        legal_actions = copy.deepcopy(possible_actions)

        return legal_actions