'''
The main program that triggers the application
'''

import argparse
import os
import sys
import traceback
import time
import copy
from threading import Lock
from state import AgentState, EnvironmentState
from datetime import datetime
from marlagent.rlagent import RLAgent
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import NSProxy
from nameserver import NameServer

pidfile = "assets/ns.pid"

def energy_request_handler(agent, message):
    # Acquire the lock
    lock.acquire()

    agent.log_info('Received: %s' % message)
    agent.log_info("Deepy copy of global state initiated...")
    curr_state = copy.deepcopy(g_agent_state)

    # update with new values of energy consumption and generation
    curr_state.time = message['time']

    # amount of requested energy
    energy_req = message['energy']

    actions = [{
        'action': 'deny_request',
        'data': energy_req
    },
    {
        'action': 'grant',
        'data': energy_req
    }
    ]

    # call get action with this new state
    action = rl_agent.get_action(copy.deepcopy(curr_state), actions)

    agent.log_info('Performing action (%s).' % action)

    # If energy request is declined
    if action['action'] ==  'deny_request':
        yield {'topic':'ENERGY_REQUEST_DECLINE'}

    # perform action and update global agent state
    next_state, energy_grant = rl_agent.do_action(curr_state, action, allies)

    # if energy request is accepted
    if action['action'] != 'deny_request':
        yield {'topic': 'ENERGY_REQUEST_ACCEPTED', 'energy': energy_grant}

    # calculate reward
    delta_reward = next_state.get_score() - curr_state.get_score()

    agent.log_info('Updating agent with reward %s.' % delta_reward)
    # update agent with reward
    rl_agent.update(state=curr_state, action=action, next_state=next_state, reward=delta_reward)

    # update the global state
    g_agent_state.energy_consumption = next_state.energy_consumption
    g_agent_state.energy_generation = next_state.energy_generation
    g_agent_state.battery_curr = next_state.battery_curr
    g_agent_state.environment_state = next_state.environment_state

    agent.log_info('Completed update operation. Resting!')

    # Release the lock
    lock.release()


def energy_consumption_handler(agent, message):
    agent.log_info('Received: %s' % message)
    yield {'topic': 'Ok'}  # immediate reply

    # Acquire the lock
    lock.acquire()

    agent.log_info("Deepy copy of global state initiated...")
    curr_state = copy.deepcopy(g_agent_state)

    # update with new values of energy consumption and generation
    curr_state.time = message['time']
    curr_state.energy_consumption += message['consumption']
    curr_state.energy_generation += message['generation']

    # call get action with this new state
    action = rl_agent.get_action(copy.deepcopy(curr_state))

    agent.log_info('Performing action (%s).' % action)
    # perform action and update global agent state
    #next_state = curr_state.get_successor_state(action)
    next_state = rl_agent.do_action(curr_state, action, allies)

    # calculate reward
    delta_reward = next_state.get_score() - curr_state.get_score()

    agent.log_info('Updating agent with reward %s.' % delta_reward)
    # update agent with reward
    rl_agent.update(state = curr_state, action = action, next_state = next_state, reward = delta_reward)

    # update the global state
    g_agent_state.energy_consumption = next_state.energy_consumption
    g_agent_state.energy_generation = next_state.energy_generation
    g_agent_state.battery_curr = next_state.battery_curr
    g_agent_state.environment_state = next_state.environment_state

    agent.log_info('Completed update operation. Resting!')

    # Release the lock
    lock.release()


def predict_energy_generation(time):
    print("TBD")
    return 0.0

def temp_handler(agent, message):
    yield {'topic' : 'Ok'} # immediate reply
    agent.log_info('Received: %s' % message['topic'])

    if message['topic'] == 'exit':
        sys.exit(0)


def initiate_nameserver(ns_socket_addr):
    pid = str(os.getpid())
    ns = None
    is_name_server_host = False

    # If file exists then nameserver has already been started. Return a reference to the name server
    if os.path.isfile(pidfile):
        print("Name server exists. Fetching reference to existing nameserver...")
        ns = NSProxy(nsaddr=ns_socket_addr)
    else:
        try :
            print("Creating a new nameserver...")
            ns = run_nameserver(addr=ns_socket_addr)
            open(pidfile, 'w+').write(pid)
            is_name_server_host = True

        except Exception:
            ns.shutdown()
            print(traceback.format_exc())
            print("ERROR: Exception caught when creating nameserver.")
            sys.exit(-1)

    return (is_name_server_host, ns)


def start_server_job(ns):
    ns_agent = NameServer(ns)

    # Start the scheduled job
    steve = run_agent('Steve', serializer='json')
    ns_agent.schedule_job(steve)


if __name__ == '__main__':

    print("Started process at ("+str(datetime.now())+")")

    parser = argparse.ArgumentParser(description='Agent Module')

    parser.add_argument('--agentname', required=True, help='Name of the agent')
    parser.add_argument('--nameserver', required=True, help='Socket address of the nameserver')
    parser.add_argument('--allies', required=True, help='Socket address of the nameserver')

    args = parser.parse_args()

    print("Hi! I am "+args.agentname+". I am taking command of this process.")

    # Initiate name server
    is_name_server_host, ns = initiate_nameserver(args.nameserver)

    lock = Lock()
    global lock

    try:

        # instantiate reinforcement learning module and making it globally accessible
        rl_agent = RLAgent()
        #global rl_agent

        # Declare a agent state and make it global
        environment_state = EnvironmentState(0.0, 0.0)
        g_agent_state = AgentState(name = args.agentname, energy_consumption = 0.0, energy_generation = 0.0,
                                   battery_curr = 0.0, time = datetime.now(), environment_state = environment_state)
        global g_agent_state

        allies = [ally for ally in args.allies.split(",") ]
        global allies

        # Initialize the agent
        agent = run_agent(name = args.agentname, nsaddr = ns.addr(), serializer='json')
        agent.bind('REP', alias='consumption', handler=energy_consumption_handler)

        if is_name_server_host:
            start_server_job(ns)


    finally:
        if is_name_server_host:
            os.unlink(pidfile)
            ns.shutdown()

        print("Bye!")


