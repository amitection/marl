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


def request_ally(ns, agent, allies, energy_amt, time):
    ally_proxy = ns.proxy(name = allies[0], timeout=1.0)
    agents = ns.agents()
    agent.log_info("AGENTSSSS__-------------:"+str(agents))
    agent.log_info(ally_proxy.ping())

    ally_proxy_addr = ally_proxy.addr(alias='energy_request')

    message = {
        'topic': 'ENERGY_REQUEST',
        'time': time,
        'energy': energy_amt
    }

    agent.log_info("Contacting ally to for: %"%message)
    resp = send_message(server_agent = agent, client_addr = ally_proxy_addr, alias = 'energy_request', message = message)

    if resp['topic'] != 'ENERGY_REQUEST_DECLINE':
        return resp['energy']
    else:
        return float(0.0)


def energy_transaction(state, next_state, borrowed_energy):
    energy_bal = get_energy_balance(state)

    if energy_bal > 0:
        next_state.energy_consumption = 0.0
        next_state.energy_generation = 0.0
        next_state.battery_curr = update_battery_status(state.battery_max, state.battery_curr,
                                                                      state.energy_generation - state.energy_consumption)

    else:
        next_state.energy_generation = 0.0
        next_state.battery_curr = 0.0
        next_state.energy_consumption = abs(energy_bal)

        if borrowed_energy > 0.0:
            next_state.energy_consumption = next_state.energy_consumption - borrowed_energy

        return next_state


def get_energy_balance(state):
    return (state.energy_generation + state.battery_curr) - state.energy_consumption


def send_message(server_agent, client_addr, alias,  message):
    server_agent.connect(client_addr, alias=alias)
    server_agent.send(alias, message=message)
    reply = server_agent.recv(alias)
    server_agent.log_info("Recieved: "+str(reply))
    server_agent.close(alias=alias)
    return reply
