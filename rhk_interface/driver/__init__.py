import dataclasses
from typing import List, Tuple
import socket
import time
import numpy as np


@dataclasses.dataclass
class Driver:
    IP_Address_R9_PC: str
    TCP_Port_R9s: int
    BUFFER_SIZE: int = 4096
    response: str = dataclasses.field(init=False, default=None)
    RETRY = 5
    BIAS_LIMIT = (0.1, 0.5)  # (V)
    CURRENT_LIMIT = (50e-12, 2000e-12)  # (A)
    IMAGE_SCAN_PROCEDURE = 'dI-dV Image Map 5.0'

    def _connect(self) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.IP_Address_R9_PC, self.TCP_Port_R9s))
        time.sleep(0.1)
        return

    def _disconnect(self) -> None:
        self.s.close()
        return

    def query(self, message: str) -> str:
        self._connect()
        self.s.send((message).encode())
        data = self.s.recv(self.BUFFER_SIZE)
        self._disconnect()
        self.response = data.decode()
        return self.response

    def get_value(self, message: str) -> float:
        retry = 0
        while retry < self.RETRY:
            try:
                value = float(self.query(message))
                break
            except:
                retry += 1
                print(f'Retry: {str(retry)}')
                time.sleep(0.1)

        return value

    def start_procedure(self, procedure: str) -> str:
        print(f"Start: {procedure}")
        self.response = self.query(f"StartProcedure, {procedure}\n")
        return self.response

    def stop_procedure(self, procedure: str) -> str:
        print(f"Stop: {procedure}")
        self.response = self.query(f"StopProcedure, {procedure}\n")
        return self.response

    def set_bias(self, value: float) -> str:
        # Set STM Bias. Value should be in unit of V. If polarity is inversed, Setpoint is also inversed.
        value = float(value)
        if np.abs(value) < self.BIAS_LIMIT[0] or np.abs(value) > self.BIAS_LIMIT[1]:
            print("Bias range over")
            return "Error"
        print(f"STM Bias is set to {value} (V)")
        self.response = self.query(f"SetSWParameter, STM Bias, Value, {str(value)}\n")
        return self.response

    def set_setpoint(self, value: float) -> str:
        value = float(value)
        # Set STM SetPoint. Value should be in unit of A. If polarity is inversed, Bias is also inversed.
        if np.abs(value) < self.CURRENT_LIMIT[0] or np.abs(value) > self.CURRENT_LIMIT[1]:
            print("SetPoint range over")
            return "Error"
        print(f"STM SetPoint is set to {value} (A)")
        self.response = self.query(f"SetHWSubParameter, Z PI Controller, Set Point, Value, {str(value)}\n")
        return self.response

    def measure_save_enable(self) -> str:
        self.response = self.query("SetSWSubItemParameter, Scan Area Window, MeasureSave, Enable, 1\n")
        return self.response

    def measure_save_disable(self) -> str:
        self.response = self.query("SetSWSubItemParameter, Scan Area Window, MeasureSave, Enable, 0\n")
        return self.response

    def get_status(self) -> str:
        self.response = self.query("GetSWParameter, Measure Item, Status\n")
        return self.response

    def get_save_index(self) -> str:
        self.response = self.query("GetSWSubItemParameter, Scan Area Window, MeasureSave, File Name Index\n")
        return self.response

    def get_save_name(self) -> str:
        self.response = self.query("GetSWSubItemParameter, Scan Area Window, MeasureSave, File Name\n")
        return self.response

    def get_save_path(self) -> str:
        self.response = self.query("GetSWSubItemParameter, Scan Area Window, MeasureSave, Save Path\n")
        return self.response

    def start_image_scan(self) -> None:
        self.start_procedure(self.IMAGE_SCAN_PROCEDURE)

    def stop_image_scan(self) -> None:
        self.stop_procedure(self.IMAGE_SCAN_PROCEDURE)

    def get_x_offset(self):
        value = self.get_value('GetSWParameter, Scan Area Window, X Offset')
        return value

    def get_y_offset(self):
        value = self.get_value('GetSWParameter, Scan Area Window, Y Offset')
        return value

    def set_x_offset(self, value: float):
        self.query(f'SetSWParameter, Scan Area Window, X Offset, {str(value)}')

    def set_y_offset(self, value: float):
        self.query(f'SetSWParameter, Scan Area Window, Y Offset, {str(value)}')

    def set_lines_per_frame(self, value: int):
        self.query(f'SetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame, {str(value)}')

    def set_line_time(self, value: float):
        self.query(f'SetSWParameter, Scan Area Window, Line Time, {str(value)}')

    def set_bias_mod(self, value: float):
        self.query(f'SetHWSubParameter, Drive CH1, Oscillation Amplitude, Value, {str(value)}')

    def set_scan_size(self, value: float):
        self.query(f'SetSWParameter, Scan Area Window, Scan Area Size, {str(value)}')
