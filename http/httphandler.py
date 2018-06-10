import requests

class HTTPHandler:

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
        self.agent_id = response.content['id']


    def update_energy_status(self, ts, energy_consumption, energy_generation):

        url = 'http://localhost:8080/energy/status'

        data = {
            "timestamp": ts,
            "agentId": self.agent_id,
            "energyGeneration": energy_consumption,
            "energyConsumption": energy_generation
        }

        response = requests.put(url=url, data=data)

        if response.status_code == 200:
            print("Energy status updated successfully with central grid.")
        else:
            print("ERROR: %s"%response.content)


    def register_transaction(self, ts, buyer_name, amount):

        url = 'http://localhost:8080/energy/trasaction'

        data = {
            "timestamp": ts,
            "sellerId": self.agent_id,
            "buyer_name": buyer_name,
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