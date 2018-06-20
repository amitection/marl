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
        self.agent_id = json.loads(response.content)['id']


    def update_energy_status(self, time, energy_consumption, energy_generation):

        url = 'http://localhost:8080/energy/status'

        data = {
            "timestamp": time,
            "agentId": self.agent_id,
            "energyGeneration": energy_consumption,
            "energyConsumption": energy_generation
        }

        response = requests.put(url=url, json=data)

        if response.status_code == 200:
            print("Energy status updated successfully with central grid.")
        else:
            print("ERROR: %s"%response.content)


    def register_transaction(self, time, buyer_name, amount):

        url = 'http://localhost:8080/energy/trasaction'

        data = {
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
            print("ERROR: %s"%response.content)


    def get_energy_status(self):
        url = 'http://localhost:8080/energy/status/grid'
        response = requests.get(url=url)

        if response.status_code == 200:
            print("Grid energy status retrieved successfully.")
            return response.content
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
            print("ERROR: %s" % response.content)


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