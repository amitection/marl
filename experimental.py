from osbrain import run_agent
from osbrain import run_nameserver
import multiprocessing


def method_a(agent, message):
    gg = mpns.temp
    gg = 10
    agent.log_info('Method A Temp: %s' % mpns.temp)
    return 'Blah 1'

def method_b(agent, message):
    agent.log_info('Method B Temp: %s' % mpns.temp)
    return 'Blah 2'


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    global mpns
    mpns = manager.Namespace()

    mpns.temp = 1

    ns = run_nameserver()

    alice = run_agent('Alice')
    bob = run_agent('Bob')

    addr1 = alice.bind('REP', alias='main1', handler=method_a)
    addr2 = alice.bind('REP', alias='main2', handler=method_b)

    bob.connect(addr1, alias='main1')
    bob.send('main1', "Some message")
    reply = bob.recv('main1')

    bob.connect(addr2, alias='main2')
    bob.send('main2', "Some message")
    reply = bob.recv('main2')
    agents = ns.agents()
    print(agents)
    ns.shutdown()

