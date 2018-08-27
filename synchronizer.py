import os
import sys
import traceback
import argparse
import time
from nameserver import NameServer
from osbrain import run_nameserver, run_agent

pidfile = "assets/ns.pid"


def initiate_nameserver(ns_socket_addr):
    osbrain_ns = None
    # If file exists then nameserver has already been started. Return a reference to the name server
    if os.path.isfile(pidfile):
        print("PID file already exists. Removing old pid file.")
        os.unlink(pidfile)

    try :
        print("Creating a new nameserver...")
        pid = str(os.getpid())
        osbrain_ns = run_nameserver(addr=ns_socket_addr)
        open(pidfile, 'w+').write(pid)

    except Exception:
        osbrain_ns.shutdown()
        print(traceback.format_exc())
        print("ERROR: Exception caught when creating nameserver.")
        sys.exit(-1)

    return osbrain_ns



def start_server_job(osbrain_ns, agentname):
    '''
    Starts the Synchronizer job to distribute energy data.
    :param osbrain_ns:
    :param agentname:
    :return:
    '''
    time.sleep(3)
    ns_agent = NameServer(osbrain_ns, agentname)

    # Start the scheduled job
    steve = run_agent(agentname, serializer='json')
    ns_agent.schedule_job(steve)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agent Module')

    parser.add_argument('--agentname', required=True, help='Name of the agent')
    parser.add_argument('--nameserver', required=True, help='Socket address of the nameserver')
    args = parser.parse_args()

    osbrain_ns = initiate_nameserver(args.nameserver)
    start_server_job(osbrain_ns, args.agentname)