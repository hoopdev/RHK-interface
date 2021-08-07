import socket
import time
import numpy as np

class Driver():
    _BUFFER_SIZE = 4096

    def __init__(self,ip_address,port):
        self.IP_Address_R9_PC = ip_address
        self.TCP_Port_R9s = port
        self.save_path = self.query("GetSWSubItemParameter, Scan Area Window, MeasureSave, Save Path\n")
        self.file_name = self.query("GetSWSubItemParameter, Scan Area Window, MeasureSave, File Name\n")

    def _connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.IP_Address_R9_PC, self.TCP_Port_R9s))
        time.sleep(0.1)
        return 

    def _disconnect(self):
        self.s.close()
        return 

    def query(self,message):
        self._connect()
        self.s.send((message).encode())
        data = self.s.recv(self._BUFFER_SIZE)
        self._disconnect()
        res = data.decode()
        return res

    def multiple_query(self,message_list):
        self._connect()
        res_list = []
        for m in message_list:
            self.s.send(m.encode())
            data = self.s.recv(self._BUFFER_SIZE)
            res = data.decode()
            res_list.append(res)
        self._disconnect()
        return res_list

    def start_procedure(self,procedure):
        print(f"Start: {procedure}")
        res = self.query(f"StartProcedure, {procedure}\n")
        return res

    def stop_procedure(self,procedure):
        print(f"Stop: {procedure}")
        res = self.query(f"StopProcedure, {procedure}\n")
        return res

    def set_bias(self,value):
        # Set STM Bias. Value should be in unit of V. If polarity is inversed, Setpoint is also inversed.
        value = float(value)
        if np.abs(value) > 1.5 or np.abs(value) < 0.1:
            print("Bias range over")
            return "Error"
        print(f"STM Bias is set to {value} (V)")
        res = self.query(f"SetSWParameter, STM Bias, Value, {str(value)}\n")
        return res

    def set_setpoint(self,value):
        value = float(value)
        # Set STM SetPoint. Value should be in unit of A. If polarity is inversed, Bias is also inversed.
        if np.abs(value) > 500e-12 or np.abs(value) < 50e-12:
            print("SetPoint range over")
            return "Error"
        print(f"STM SetPoint is set to {value} (A)")
        res = self.query(f"SetHWSubParameter, Z PI Controller, Set Point, Value, {str(value)}\n")
        return res

    def measure_save_enable(self):
        res = self.query("SetSWSubItemParameter, Scan Area Window, MeasureSave, Enable, 1\n")
        return res

    def measure_save_disable(self):
        res = self.query("SetSWSubItemParameter, Scan Area Window, MeasureSave, Enable, 0\n")
        return res

    def get_status(self):
        res = self.query("GetSWParameter, Measure Item, Status\n")
        return res
    
    def get_save_index(self):
        res = self.query("GetSWSubItemParameter, Scan Area Window, MeasureSave, File Name Index\n")
        return res
