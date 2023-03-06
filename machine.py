"""Module for the time_machine class. 
Runs a spreadsheet-like data at even time steps as if it were online.
"""

import datetime
import time
import re
from pathlib import Path

import opcua # type: ignore
import pandas as pd # type: ignore
import easygui # type: ignore



class TimeMachine:
    """class object for the time machine"""
    def __init__(self):
        self.data_path = None
        self.interval_seconds = 60
        self.opc_server = None
        self.opc_index = None
        self.dataframe = None
        self.opc_var_names = None
        self.opc_vars = None

        self.opc_configured_flag = False
        self.opc_run_flag = False

    def select_data(self):
        """Choose a dataset to run in the machine"""
        path = Path(easygui.fileopenbox())
        self.data_path = path
        raw_dataframe = self._load_data(path)
        regex = re.compile('^(?!.*time).*', flags = re.IGNORECASE)
        self.dataframe = raw_dataframe.filter(regex=regex, axis=1)
        self.opc_var_names = ["Time"] + list(self.dataframe.columns)
        # return path

    def _load_data(self, path):
        """Loads the data from the file into memory"""

        if path.suffix in [".xls", ".xlsx"]:
            return pd.read_excel(path)
        if path.suffix in [".csv"]:
            return pd.read_csv(path)

        raise ValueError

    def configure(self, interval_seconds: int):
        """Choose parameters for this time machine"""
        self.interval_seconds = interval_seconds

    def run(self):
        """Start running the time machine"""
        # some sort of while loop?

    def create_opc_server(self, ip_address = "96.125.117.229:4841"):
        """Creates the OPC server with opcua python"""
        server = opcua.Server()
        server.set_server_name("OpcUa Time Machine")
        server.set_endpoint(f"opc.tcp://{ip_address}")
        idx = server.register_namespace(f"http://{ip_address}")
        self.opc_server = server
        self.opc_index = idx
        # return server, idx

    def configure_opc(self):
        """Config and setup for the opc instance"""
        objects = self.opc_server.get_objects_node()
        myobject = objects.add_object(self.opc_index, "Time Machine")

        # tag_list = {"Temperature":25, "Windspeed":11, "Flowrate":1}
        myvars = []

        for var in self.opc_var_names:
            myvar = myobject.add_variable(self.opc_index, var, 0)
            myvar.set_writable(writable=True)
            myvars.append(myvar)

        self.opc_vars = myvars
        self.opc_configured_flag = True

    def start_opc(self):
        """Start the opc server"""
        if self.opc_configured_flag and not self.opc_run_flag:
            self.opc_server.start()
            self.opc_run_flag = True

    def update_opc(self, row):
        """Send an update to the opc server"""
        if self.opc_run_flag:
            row_columns = row.index
            now = pd.Series([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")], index=["Time"])
            row = pd.concat([row,now])
            new_cols = ["Time"] + list(row_columns)
            row = row[new_cols]
            try:
                for opc_var_index, var in enumerate(self.opc_vars):
                    var.set_value(row[opc_var_index])
            except AttributeError as error:
                print(error)

    def stop_opc(self):
        """Stop the opc server"""
        if self.opc_run_flag:
            self.opc_server.stop()
            self.opc_run_flag = False

    def run_time_machine(self):
        """This implements the loop that runs the dataframe through the opc server"""
        end = self.dataframe.shape[0]
        row_number = 0
        while row_number < end:
            self.update_opc(self.dataframe.iloc[row_number, :])
            time.sleep(self.interval_seconds)
            row_number = row_number + 1
    