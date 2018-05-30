'''
The main program that triggers the application
'''

import argparse
import os
import sys
import traceback
from datetime import datetime
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import NSProxy

from nameserver import NameServer

pidfile = "assets/ns.pid"


def exit_handler(is_server, ns):
    os.unlink(pidfile)
    ns.shutdown()


def energy_request_handler(agent, message):
    agent.log_info('Received: %s' % message['test'])


def energy_consumption_handler(agent, message):
    agent.log_info('Received: %s' % message['test'])


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

    args = parser.parse_args()

    print("Hi! I am "+args.agentname+". I am taking command of this process.")

    # Initiate name server
    is_name_server_host, ns = initiate_nameserver(args.nameserver)

    try:
        # Initialize the agent
        agent = run_agent(name = args.agentname, nsaddr = ns.addr(), serializer='json')
        agent.bind('REP', alias='consumption', handler=temp_handler)

        if is_name_server_host:
            start_server_job(ns)


    finally:
        if is_name_server_host:
            os.unlink(pidfile)
            ns.shutdown()

        print("Bye!")


