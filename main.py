'''
The main program that triggers the application
'''

import argparse
import os
import sys
import traceback
import time
import copy
import _thread
import util
import multiprocessing
from random import randint
from state import AgentState, EnvironmentState
from datetime import datetime
from marlagent.agent.linear.lin_agent import LinearQAgent
from marlagent.agent.dqn.dqn import DQNAgent
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import NSProxy
from nameserver import NameServer
from cghandler import httpservice
from prediction.energy_generation import EnergyGeneration


pidfile = "assets/ns.pid"

def exit_check(msg):
    if msg['topic'] == 'exit':
        return True


def energy_request_handler(agent, message):

    # Acquire the lock
    lock_count = 0
    while not multiprocessing_lock.acquire(blocking=False):
        try:
            if lock_count <= 2:
                time.sleep(randint(1, 3) / 10)
                lock_count += 1
            else:
                yield {'topic': 'ENERGY_REQUEST_DECLINE'}
                agent.log_info("Could not acquire lock! Energy request declined.")
                return
        except:
            print(traceback.format_exc())


    agent.log_info("Lock Acquired!")

    try:
        print("-----------------------Start Transaction-----------------------")
        agent.log_info('Received: %s' % message)

        agent.log_info("Deepy copy of global state initiated...")
        l_g_agent_state = multiprocessing_ns.g_agent_state
        l_curr_state = copy.deepcopy(l_g_agent_state)

        # update with new values of energy consumption and generation
        l_curr_state.time = datetime.strptime(message['time'], '%Y/%m/%d %H:%M')

        # amount of requested energy
        energy_req = message['energy']

        actions = [
            {
                'action': 'grant',
                'data': energy_req
            },
            {
                'action': 'deny_request',
                'data': energy_req
            }
        ]

        # call get action with this new state
        l_rl_agent = multiprocessing_ns.rl_agent
        action = l_rl_agent.get_action(copy.deepcopy(l_curr_state), actions)

        agent.log_info('Performing action (%s).' % action)

        response = None

        # If energy request is declined
        if action['action'] ==  'deny_request':
            response = {'topic':'ENERGY_REQUEST_DECLINE'}

        # perform action and update global agent state
        next_state, energy_grant = l_rl_agent.do_action(l_curr_state, action, osbrain_ns, agent, args.agentname, allies)

        # if energy request is accepted
        if action['action'] == 'grant':
            response = {'topic': 'ENERGY_REQUEST_ACCEPTED', 'energy': energy_grant}
            agent.log_info("GRANTING:-----:%s"%energy_grant)
            next_state.environment_state.update_energy_granted_to_ally(energy_grant)
            print("BATTERY AFTER GRANTING-----:%s"%next_state.battery_curr)

            _thread.start_new_thread(cg_http_service.register_transaction, (message['time'],
                                                                           message['agentName'],
                                                                           energy_grant))

        # Get grid status from CG
        # curr_grid_status = cg_http_service.get_energy_status(l_curr_state.iter)
        # net_curr_grid_status = util.calc_net_grid_status(curr_grid_status)

        # calculate reward
        # delta_reward = next_state.get_score() + util.reward_transaction(l_curr_state, next_state, action, net_curr_grid_status)

        # agent.log_info('Updating agent with delta reward %s.' % delta_reward)
        # update agent with reward

        l_rl_agent.update(state=l_curr_state, action=action, next_state=next_state, reward=0.0, eoi = False)

        # Update grid status
        # next_state.environment_state.net_grid_status = net_curr_grid_status

        # update the global state
        l_g_agent_state.energy_consumption = 0.0
        l_g_agent_state.energy_generation = 0.0
        l_g_agent_state.battery_curr = next_state.battery_curr
        l_g_agent_state.environment_state = next_state.environment_state

        agent.log_info('Completed update operation. Resting!')

        # agent.log_info(next_state)
        agent.log_info(l_g_agent_state.environment_state)

        print("-----------------------End of Transaction-----------------------\n\n\n")

        # Synchronize Objects
        multiprocessing_ns.g_agent_state = l_g_agent_state
        multiprocessing_ns.rl_agent = l_rl_agent
        agent.log_info("Finished synchronizing objects across forked processes.")

        yield response
    except Exception:
        print(traceback.format_exc())
        yield {'topic': 'ENERGY_REQUEST_DECLINE'}

    finally:
        # Release the lock
        multiprocessing_lock.release()
        agent.log_info("Lock Released!")


def energy_consumption_handler(agent, message):
    yield {'topic': 'Ok'}  # immediate reply

    # Exit check
    if exit_check(message):
        sys.exit(0)

    global osbrain_ns

    if message['topic'] == 'ENERGY_CONSUMPTION':
        _thread.start_new_thread(invoke_agent_ec_handle, (agent, osbrain_ns, message))

    elif message['topic'] == 'END_OF_ITERATION' or message['topic'] == 'TRAINING_COMPLETE':
        _thread.start_new_thread(eoi_handle, (agent, message))


def invoke_agent_ec_handle(agent, osbrain_ns, message):

    try:
        print("Trying to acquire lock!")
        # Acquire the lock
        multiprocessing_lock.acquire()
    except Exception:
        print(traceback.format_exc())
        return

    print("\n-----------------------Start Transaction-----------------------")
    agent.log_info('Received: %s' % message)

    try:
        agent.log_info("Deepy copy of global state initiated...")
        l_g_agent_state = multiprocessing_ns.g_agent_state
        l_curr_state = copy.deepcopy(l_g_agent_state)

        # update with new values of energy consumption and generation
        l_curr_state.time = datetime.strptime(message['time'], '%Y/%m/%d %H:%M')

        # Get energy generation
        energy_generated = energy_generator.get_generation(l_curr_state.time)

        l_curr_state.energy_consumption = message['consumption']
        l_curr_state.energy_generation = energy_generated


        # call get action with this new state
        l_rl_agent = multiprocessing_ns.rl_agent
        action = l_rl_agent.get_action(copy.deepcopy(l_curr_state))

        agent.log_info('Performing action (%s).' % action)
        # perform action and update global agent state
        next_state, usable_generated_energy = l_rl_agent.do_action(l_curr_state, action, osbrain_ns, agent, args.agentname, allies)

        agent.log_info('Action complete. Registering action effect with the environment.')

        # Registering information to CG
        _thread.start_new_thread(cg_http_service.update_energy_status, (message['time'],
                                                                        message['iter'],
                                                                        float(args.battInit),
                                                                        message['consumption'],
                                                                        usable_generated_energy,
                                                                        next_state.environment_state.get_energy_borrowed_from_CG()
                                                                        - l_curr_state.environment_state.get_energy_borrowed_from_CG()))


        delta_reward = 0.0
        # Get grid status from CG
        # curr_grid_status = cg_http_service.get_energy_status(l_curr_state.iter)
        # net_curr_grid_status = util.calc_net_grid_status(curr_grid_status)

        # calculate reward
        # delta_reward = next_state.get_score() + util.reward_transaction(l_curr_state, next_state, action,
        #                                                                 net_curr_grid_status)


        agent.log_info('Updating agent with reward %s.' % delta_reward)
        l_rl_agent.update(state=l_curr_state, action=action, next_state=next_state, reward=0.0)

        # Update grid status
        # next_state.environment_state.net_grid_status = net_curr_grid_status

        # update the global state
        l_g_agent_state.energy_consumption = 0.0
        l_g_agent_state.energy_generation = 0.0
        l_g_agent_state.battery_curr = next_state.battery_curr
        l_g_agent_state.environment_state = next_state.environment_state

        # agent.log_info(next_state)
        # agent.log_info(l_g_agent_state.environment_state)
        agent.log_info('Completed update operation. Resting!')
        print("-----------------------End of Transaction-----------------------\n\n")

        # Synchronize Objects
        multiprocessing_ns.g_agent_state = l_g_agent_state
        multiprocessing_ns.rl_agent = l_rl_agent
        agent.log_info("Finished synchronizing objects across forked processes.")

    except Exception:
        print(traceback.format_exc())

    finally:
        # Release the lock
        multiprocessing_lock.release()
        agent.log_info("Lock Released!")


def eoi_handle(agent, message):
    '''
    End of iteration handler.
    :return:
    '''
    multiprocessing_lock.acquire()
    global g_env_state
    try:
        print("\n\n\-----------------------Iteration (%s) Completed-----------------------\n\n"%message['iter'])

        # Fetching Reference
        l_rl_agent = multiprocessing_ns.rl_agent
        l_g_agent_state = multiprocessing_ns.g_agent_state
        g_env_state = l_g_agent_state.environment_state


        agent.log_info("Publishing Stats...")
        agent.log_info(g_env_state)

        nzeb_status = (g_env_state.get_total_generated() + g_env_state.get_energy_borrowed_from_ally()) \
                      - (g_env_state.get_total_consumed() + g_env_state.get_energy_borrowed_from_CG())
        agent.log_info("NZEB Status: %s" % nzeb_status)


        # Log EOI details to CG
        cg_http_service.log_iteration_status(message['iter'], g_env_state, nzeb_status)


        # --------------------- Updating reward ---------------------
        agent.log_info('Calculating reward.')

        # Get grid status from CG
        curr_grid_status = cg_http_service.get_energy_status(int(message['iter']))
        net_curr_grid_status = util.calc_net_grid_status(curr_grid_status)

        # calculate reward
        # delta_reward = util.compare(net_curr_grid_status, multiprocessing_ns.old_grid_status)


        # If this grid status is better than the previous best grid status
        # if util.compare(net_curr_grid_status, multiprocessing_ns.best_grid_status) > 1 :
        #     multiprocessing_ns.best_grid_status = net_curr_grid_status
        #     delta_reward += 3

        # delta_reward = delta_reward - abs(int(multiprocessing_ns.best_grid_status - net_curr_grid_status)) * 0.1

        # multiprocessing_ns.old_grid_status = net_curr_grid_status

        delta_reward = util.reward_transaction(state = None, next_state = None, action = None, net_curr_grid_status = net_curr_grid_status)
        l_rl_agent.update(state=None, action=None, next_state=None, reward=delta_reward, eoi = True)
        #---------------------------------------------------------------


        if int(message['iter']) > 0 and int(message['iter']) % 50 == 0:
            l_rl_agent.epsilon = round(l_rl_agent.epsilon * 0.8, 5)
            agent.log_info("Updated Epsilon: %s"%l_rl_agent.epsilon)


        # If training phase done then set exploration to 0
        # i.e. complete exploitation
        if message['topic'] == 'TRAINING_COMPLETE':
            l_rl_agent.epsilon = 0.0


        # reset the agent global state
        print(".......................RESETTING GLOBAL STATE.......................")
        l_g_agent_state.reset(float(args.battInit))
        l_g_agent_state.iter = int(message['iter']) + 1
        agent.log_info(l_g_agent_state.environment_state)


        # Synchronize Objects
        multiprocessing_ns.rl_agent = l_rl_agent
        multiprocessing_ns.g_agent_state = l_g_agent_state
        agent.log_info("Finished synchronizing objects across forked processes.")

    except Exception:
        print(traceback.format_exc())

    finally:
        # Release the lock
        multiprocessing_lock.release()

def predict_energy_generation(time):
    print("TBD")
    return 0.0


def get_ref_to_nameserver(ns_socket_addr):
    osbrain_ns = None
    print("Fetching reference to existing nameserver...")
    osbrain_ns = NSProxy(nsaddr=ns_socket_addr)
    return osbrain_ns


def start_server_job(osbrain_ns):
    time.sleep(2)
    ns_agent = NameServer(osbrain_ns)

    # Start the scheduled job
    steve = run_agent('Steve', serializer='json')
    ns_agent.schedule_job(steve)


def args_handler():
    parser = argparse.ArgumentParser(description='Agent Module')

    parser.add_argument('--agentname', required=True, help='Name of the agent')
    parser.add_argument('--nameserver', required=True, help='Socket address of the nameserver')
    parser.add_argument('--allies', required=False, help='Socket address of the nameserver')
    parser.add_argument('--battInit', required=True, help='Initial battery charge.')
    parser.add_argument('--solarexposure', required=False, help='Path to solar exposure dataset')
    parser.add_argument('--nSolarPanel', required=True, help='Number fo solar panel this house has')

    global args
    args = parser.parse_args()

    if args.solarexposure is None:
        args.solarexposure = 'assets/toronto_solar_exp_2011.csv'


if __name__ == '__main__':

    print("Started process at ("+str(datetime.now())+")")
    args_handler()

    print("Hi! I am "+args.agentname+". I am taking command of this process.")

    # Initiate name server
    global osbrain_ns
    osbrain_ns = get_ref_to_nameserver(args.nameserver)

    global cg_http_service
    cg_http_service = httpservice.CGHTTPHandler(args.agentname)

    try:
        from osbrain.logging import pyro_log
        pyro_log()

        # instantiate reinforcement learning module and making it globally accessible
        global multiprocessing_ns, multiprocessing_lock
        manager = multiprocessing.Manager()
        multiprocessing_ns = manager.Namespace()
        multiprocessing_lock = manager.RLock()

        multiprocessing_ns.rl_agent = DQNAgent()
        # multiprocessing_ns.rl_agent = LinearQAgent()

        global energy_generator
        energy_generator = EnergyGeneration(args.solarexposure, float(args.nSolarPanel))

        # Declare a agent state and make it global
        environment_state = EnvironmentState(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        # global g_agent_state
        multiprocessing_ns.g_agent_state = AgentState(name = args.agentname, iter = 0, energy_consumption = 0.0, energy_generation = 0.0,
                                   battery_curr = float(args.battInit), time = '2014/01/01 12:00', environment_state = environment_state,
                                   cg_http_service = cg_http_service)

        multiprocessing_ns.old_grid_status = -99999
        multiprocessing_ns.best_grid_status = -99999

        global allies
        allies = [ally for ally in args.allies.split(",") ]
        # allies = []

        # Initialize the agent
        agent = run_agent(name = args.agentname, nsaddr = osbrain_ns.addr(), serializer='json', transport='tcp')
        agent.bind('REP', alias=str('energy_request_'+args.agentname), handler=energy_request_handler)
        agent.bind('REP', alias='consumption', handler=energy_consumption_handler)



    except Exception:
        print(traceback.format_exc())


    finally:

        while(1):
            time.sleep(1)

        print("Bye!")


