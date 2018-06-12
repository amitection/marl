import util
import pandas as pd
from datetime import datetime

class EnergyGeneration:

    def __init__(self, path_to_file, n_solar_panel):

        self.n_solar_panel = n_solar_panel

        time = []
        dni = [] # Values are w/m2
        self.D = pd.read_csv(path_to_file, sep=',', usecols=['Year', 'Month', 'Day', 'Hour', 'Minute', 'DNI'])

        for index, row in self.D.iterrows():
            ts = "{0}/{1:02d}/{2:02d} {3:02d}:{4:02d}".format(row['Year'], row['Month'], row['Day'], row['Hour'], row['Minute'])
            time.append(ts)
            dni.append(row['DNI'])

        d = {'Time':time, 'DNI': dni}
        self.D = pd.DataFrame(data=d)

        print("Solar exposure data loaded successfully.")


    def get_generation(self, ts):
        """
        Get the generation at a particular time in kWh. It is assumed that solar exposure at a particular time has been
        predicted.
        :param ts:
        :return: kWh
        """
        ts_str = util.cnv_datetime_to_str(ts, '%m/%d %H:%M')
        data = self.D.loc[self.D['Time'].str.contains(ts_str)]

        unit_generation = self._calculate_generation(exposure=float(data['DNI'].values[0]))
        total_generation = (unit_generation * self.n_solar_panel) / 1000.0
        print("TOTAL GENERATION"+str(total_generation))
        return total_generation


    def _calculate_generation(self, exposure, max_cap = 180.0):
        return max_cap * (exposure / 1000.0)