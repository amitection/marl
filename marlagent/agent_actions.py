from osbrain import NSProxy

def update_battery_status(battery_max, battery_curr, amount):
    '''
    Update the battery status
    :param battery_max:
    :param battery_curr:
    :param amount:
    :return: the new current battery status
    '''
    battery_cap_left = battery_max - battery_curr
    new_batt_status = battery_curr

    if amount <= 0.0 and abs(amount) <= battery_curr:
        new_batt_status += amount

    elif amount <= 0.0 and abs(amount) > battery_curr:
        new_batt_status = 0.0

    elif amount > 0.0 and battery_cap_left >= amount:
        new_batt_status += amount
    elif amount > 0.0 and battery_cap_left < amount:
        new_batt_status += battery_cap_left

    print("Battery status updated: %s." % new_batt_status)
    return new_batt_status


def request_ally(ns, agent, agent_name, allies, energy_amt, time):
    ally_proxy = ns.proxy(name = allies[0], timeout=1.0)
    ally_proxy_addr = ally_proxy.addr(alias=str('energy_request_'+allies[0]))

    message = {
        'topic': 'ENERGY_REQUEST',
        'agentName':agent_name,
        'time': time,
        'energy': energy_amt
    }

    agent.log_info("Contacting ally for: %s"%message)
    resp = send_message(agent = agent, server_addr = ally_proxy_addr, alias = str('energy_request_'+allies[0]), message = message)

    if resp['topic'] != 'ENERGY_REQUEST_DECLINE':
        return resp['energy']
    else:
        return float(0.0)


def energy_transaction(next_state):

    next_state.energy_consumption = 0.0
    next_state.energy_generation = 0.0
    next_state.battery_curr = 0.0

    return next_state


def get_energy_balance(state):
    return (state.energy_generation + state.battery_curr) - state.energy_consumption


def send_message(agent, server_addr, alias,  message):
    agent.log_info('My Addr---------:%s'%agent)
    agent.log_info('Server Addr---------:%s'%server_addr)
    agent.connect(server=server_addr, alias=alias)
    agent.send(alias, message=message)
    reply = agent.recv(alias)
    agent.log_info("Recieved: "+str(reply))
    agent.close(alias=alias)
    return reply
