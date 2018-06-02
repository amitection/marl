import time
import pandas as pd
from osbrain import run_agent
from datetime import datetime

class NameServer:
    def __init__(self, ns):
        print("Instantiating NameServer class...")

        self.ns = ns
        time.sleep(5) # to let all the agents load due to startup latency


    def _load_data(self, path_to_file):
        '''
        Import data from the specified directory
        :param path_to_file:
        :return:
        '''
        dateparse = lambda dates: pd.datetime.strptime(dates, '%m/%d/%Y %I:%M %p')
        D = pd.read_csv(path_to_file, sep=';', parse_dates=['Time'], date_parser=dateparse)
        return D

    def schedule_job(self, server_agent):
        d1 = self._load_data("assets/house1_consumption.csv")
        d2 = self._load_data("assets/house1_consumption.csv")

        # extracting the list of agents
        agents = self.ns.agents()

        alice = self.ns.proxy('Alice')
        bob = self.ns.proxy('Bob')

        alice_addr = alice.addr(alias='consumption')
        bob_addr = bob.addr(alias='consumption')

        message = {
            'topic': 'ENERGY_CONSUMPTION',
            'time': datetime.now(),
            'consumption': 0.0
        }

        try :
            for timestep in range(1051230, 2103810, 30):
                d1_consumption = d1.loc[d1['Electricity.Timestep'] == timestep]
                d2_consumption = d2.loc[d2['Electricity.Timestep'] == timestep]

                message['time'] = d1_consumption['Time']

                message['consumption'] = float(d1_consumption['Sum [kWh]'])
                self._send_message(server_agent, alice_addr, alias='consumption', message=message)

                message['consumption'] = float(d2_consumption['Sum [kWh]'])
                self._send_message(server_agent, bob_addr, alias='consumption', message=message)

                time.sleep(3)
        finally:
            # Safe shutdown of all agents for testing
            self._send_message(server_agent, alice_addr, alias='consumption', message={'topic': 'exit'})
            self._send_message(server_agent, bob_addr, alias='consumption', message={'topic': 'exit'})


    def _send_message(self, server_agent, client_addr, alias,  message):
        server_agent.connect(client_addr, alias=alias)
        server_agent.send(alias, message=message)
        reply = server_agent.recv(alias)
        server_agent.log_info("Recieved: "+str(reply))
        server_agent.close(alias=alias)