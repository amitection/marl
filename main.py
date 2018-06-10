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
import _thread

pidfile = "assets/ns.pid"

def exit_check(msg):
    if msg['topic'] == 'exit':
        return True


def energy_request_handler(agent, message):

    lock.acquire()

    # Acquire the lock
    lock_count = 0
    # while not lock.acquire():
    #     if lock_count <= 2:
    #         time.sleep(randint(1, 10) / 10)
    #         lock_count += 1
    #     else:
    #         return {'topic': 'ENERGY_REQUEST_DECLINE'}

    print("-----------------------Start Transaction-----------------------")
    agent.log_info('Received: %s' % message)

    agent.log_info("Deepy copy of global state initiated...")
    curr_state = copy.deepcopy(g_agent_state)

    # update with new values of energy consumption and generation
    curr_state.time = datetime.strptime(message['time'], '%Y/%m/%d %H:%M')

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
    next_state, energy_grant = rl_agent.do_action(curr_state, action, ns, agent, allies)

    # if energy request is accepted
    if action['action'] != 'deny_request':
        yield {'topic': 'ENERGY_REQUEST_ACCEPTED', 'energy': energy_grant}

    # calculate reward
    delta_reward = next_state.get_score() - curr_state.get_score()

    agent.log_info('Updating agent with delta reward %s.' % delta_reward)
    # update agent with reward
    rl_agent.update(state=curr_state, action=action, next_state=next_state, reward=delta_reward)

    # update the global state
    g_agent_state.energy_consumption = next_state.energy_consumption
    g_agent_state.energy_generation = next_state.energy_generation
    g_agent_state.battery_curr = next_state.battery_curr
    g_agent_state.environment_state = next_state.environment_state

    agent.log_info('Completed update operation. Resting!')

    print("-----------------------End of Transaction-----------------------\n\n\n")
    # Release the lock
    lock.release()


def energy_consumption_handler(agent, message):
    yield {'topic': 'Ok'}  # immediate reply

    _thread.start_new_thread(invoke_agent_ec_handle, (agent, ns, message))


def invoke_agent_ec_handle(agent, ns, message):
    # Acquire the lock
    lock.acquire()

    print("-----------------------Start Transaction-----------------------")
    agent.log_info('Received: %s' % message)

    # Exit check
    if exit_check(message):
        lock.release()
        sys.exit(0)

    try:
        agent.log_info("Deepy copy of global state initiated...")
        curr_state = copy.deepcopy(g_agent_state)

        # update with new values of energy consumption and generation
        curr_state.time = datetime.strptime(message['time'], '%Y/%m/%d %H:%M')
        curr_state.energy_consumption = message['consumption']
        curr_state.energy_generation = message['generation']
        curr_state.environment_state.set_total_consumed(message['consumption'])
        curr_state.environment_state.set_total_generated(message['generation'])

        # call get action with this new state
        action = rl_agent.get_action(copy.deepcopy(curr_state))

        agent.log_info('Performing action (%s).' % action)
        # perform action and update global agent state
        next_state = rl_agent.do_action(curr_state, action, ns, agent, allies)

        agent.log_info('Action complete. Calculating reward.')
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

        agent.log_info(g_agent_state)
        agent.log_info(g_agent_state.environment_state)
        agent.log_info('Completed update operation. Resting!')

    except Exception:
        print(traceback.format_exc())

    finally:
        # Release the lock
        lock.release()
        print("-----------------------End of Transaction-----------------------\n\n\n")


def predict_energy_generation(time):
    print("TBD")
    return 0.0


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
    time.sleep(2)
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
    global ns
    is_name_server_host, ns = initiate_nameserver(args.nameserver)

    global lock
    lock = Lock()
    global lock_count
    lock_count = 0

    try:
        from osbrain.logging import pyro_log
        pyro_log()

        # instantiate reinforcement learning module and making it globally accessible
        global rl_agent
        rl_agent = RLAgent()

        # Declare a agent state and make it global
        environment_state = EnvironmentState(0.0, 0.0, 0.0, 0.0)
        global g_agent_state
        g_agent_state = AgentState(name = args.agentname, energy_consumption = 0.0, energy_generation = 0.0,
                                   battery_curr = 0.0, time = datetime.now(), environment_state = environment_state)

        global allies
        allies = [ally for ally in args.allies.split(",") ]

        # Initialize the agent
        agent = run_agent(name = args.agentname, nsaddr = ns.addr(), serializer='json', transport='tcp')
        agent.bind('REP', alias=str('energy_request_'+args.agentname), handler=energy_request_handler)
        agent.bind('REP', alias='consumption', handler=energy_consumption_handler)

        if is_name_server_host:
            start_server_job(ns)

    finally:
        if is_name_server_host:
            os.unlink(pidfile)
        #     ns.shutdown()

        print("Bye!")


