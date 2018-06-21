import time
import util
import traceback
import pandas as pd
from osbrain import run_agent
from datetime import datetime

class NameServer:
    def __init__(self, ns, agentname):
        print("Instantiating NameServer class...")

        self.ns = ns
        self.agentname = agentname
        time.sleep(5) # to let all the agents load due to startup latency


    def schedule_job(self, server_agent):
        self.d1 = self._load_data("assets/house1_consumption.csv")
        self.d2 = self._load_data("assets/house2_consumption.csv")

        d_map = {
            "Alice": self.d1,
            "Bob": self.d2,
            "Charlie": self.d1
        }

        # extracting the list of agents
        agents = self.ns.agents()
        server_agent.log_info("Registering client details...")
        agent_name_arr, agent_addr = self.extract_agents(agents)
        server_agent.log_info("Registered clients: %s"%agent_addr)


        message = {
            'topic': 'ENERGY_CONSUMPTION',
            'time': datetime.now().strftime('%Y/%m/%d %H:%M'),
            'iter': 0,
            'consumption': 0.0,
            'generation': 0.0
        }

        for iter in range(50):
            message['iter'] = iter

            last_message = self.dispatch_energy_data(server_agent, message, agent_name_arr, agent_addr, d_map)
            server_agent.log_info("Iteration (%s) complete!"%iter)

            eoi_message = {
                'topic': 'END_OF_ITERATION',
                'iter': iter,
                'time': last_message['time']
            }

            # EOI: notify each agent to save its status at the end of each iteration
            for name in agent_name_arr:
                self._send_message(server_agent, agent_addr[name], alias='consumption', message=eoi_message)
            time.sleep(3)


        # Exit Message after iterations done
        # Safe shutdown of all agents for testing
        for name in agent_name_arr:
            self._send_message(server_agent, agent_addr[name], alias='consumption', message={'topic': 'exit'})


    def _load_data(self, path_to_file):
        '''
        Import data from the specified directory
        :param path_to_file:
        :return:
        '''
        dateparse = lambda dates: pd.datetime.strptime(dates, '%m/%d/%Y %I:%M %p')
        D = pd.read_csv(path_to_file, sep=';', parse_dates=['Time'], date_parser=dateparse)
        D = D.set_index(D['Electricity.Timestep'])
        return D


    def dispatch_energy_data(self, server_agent, message, agent_name_arr, agent_addr, d_map):

        try:
            # for timestep in range(0, 150, 30):
            for timestep in range(0, 4290, 30):

                for name in agent_name_arr:
                    d = d_map[name]
                    d_consumption = d.loc[d['Electricity.Timestep'] == timestep]

                    message['time'] = util.cnv_datetime_to_str(d_consumption['Time'].get(timestep), '%Y/%m/%d %H:%M')

                    message['consumption'] = float(d_consumption['Sum [kWh]'])
                    message['generation'] = float(
                        util.get_generation(d_consumption['Time'].get(timestep), message['consumption']))

                    self._send_message(server_agent, agent_addr[name], alias='consumption', message=message)

                time.sleep(2)

        except Exception:
            print(traceback.format_exc())

        return message


    def extract_agents(self, agents):

        agent_name_arr = []
        agent_addr = {}
        for name in agents:
            if name != self.agentname:
                agent_name_arr.append(name)
                agent = self.ns.proxy(name)
                agent_addr[name] = agent.addr(alias='consumption')

        return agent_name_arr, agent_addr


    def _send_message(self, server_agent, client_addr, alias,  message):

        server_agent.connect(client_addr, alias=alias)
        server_agent.send(alias, message=message)
        reply = server_agent.recv(alias)
        server_agent.log_info("Recieved: "+str(reply))
        server_agent.close(alias=alias)

