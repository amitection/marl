import requests
import json

class CGHTTPHandler:

    def __init__(self, agent_name):
        self.agent_name = agent_name
        self._register_agent()


    def _register_agent(self):
        print("Registering Agent with Central Monitor...")

        url = 'http://localhost:8080/agent/register'
        data = {
            "name": self.agent_name,
            "active": True
        }

        response = requests.post(url=url, json=data)
        self.agent_id = json.loads(response.content.decode('utf-8'))['id']


    def update_energy_status(self, time, iter, batt_init, energy_consumption, energy_generation, borrowed_from_CG):

        url = 'http://localhost:8080/energy/status'

        data = {
            "timestamp": time,
            "agentId": self.agent_id,
            "iter": iter,
            "batteryInitial": batt_init,
            "energyConsumption": energy_consumption,
            "energyGeneration": energy_generation,
            "borrowedFromCG": borrowed_from_CG
        }
        print(data)
        response = requests.put(url=url, json=data)

        if response.status_code == 200:
            print("Energy status updated successfully with central grid.")
        else:
            print("ERROR: %s"%response.content.decode('utf-8'))


    def register_transaction(self, iter, time, buyer_name, amount):

        url = 'http://localhost:8080/energy/trasaction'

        data = {
            "iter": iter,
            "timestamp": time,
            "sellerId": self.agent_id,
            "buyerName": buyer_name,
            "price": 0.5,
            "amount": amount
        }

        response = requests.post(url=url, json=data)

        if response.status_code == 200:
            print("Energy transaction successfully registered with central grid.")
        else:
            print("ERROR: %s"%response.content.decode('utf-8'))


    def get_energy_status(self, iter):
        url = 'http://localhost:8080/energy/status/grid/'+str(iter)
        response = requests.get(url=url)

        if response.status_code == 200:
            print("Grid energy status retrieved successfully.")
            return json.loads(response.content.decode('utf-8'))
        else:
            print("ERROR: Error retrieving grid energy status. %s"%response.content)
            return None


    def log_iteration_status(self, iter, env, nzeb_status):
        url = 'http://localhost:8080/energy/log/iteration/status'

        data = {
            "iteration": iter,
            "agentId": self.agent_id,
            "energyGeneration": env.get_total_generated(),
            "energyConsumption": env.get_total_consumed(),
            "energyBorrowedFromAlly": env.get_energy_borrowed_from_ally(),
            "energyBorrowedFromCG": env.get_energy_borrowed_from_CG(),
            "nzebStatus": nzeb_status
        }

        response = requests.post(url=url, json=data)

        if response.status_code == 200:
            print("Iteration status successfully logged to central grid.")
        else:
            print("ERROR: %s" % response.content.decode('utf-8'))


instance = False
cg_http_handler = None

def get_CG_serivce_instance(agent_name):

    global instance
    if not instance:
        global cg_http_handler
        cg_http_handler = CGHTTPHandler(agent_name)
        instance = True
        return cg_http_handler
    else:
        return cg_http_handler