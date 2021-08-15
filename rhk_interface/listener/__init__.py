import dataclasses
import socket
import numpy as np
from ctypes import *


@dataclasses.dataclass
class Listener:
    IP_Address: str
    BUFFER_SIZE: int = 2048
    FORMAT: dict = {
        'packet_len': c_uint32,
        'timestamp': c_uint64,
        'interval': c_float,
        'gain': c_float,
        'label_size': c_uint32,
        'label': c_char,
        'unit_size': c_uint32,
        'unit': c_char,
        'data_size': c_uint32,
        'data': c_int32
    }
    offset: int = dataclasses.field(init=False, default=None)
    length: dict = {
        'packet_len': 4,
        'timestamp': 8,
        'interval': 4,
        'gain': 4,
        'label_size': 4,
        'label': None,
        'unit_size': 4,
        'unit': None,
        'data_size': 4,
        'data': None,
    }
    result: dict = dataclasses.field(init=False, default=None)
    response_address: str = dataclasses.field(init=False, default=None)
    value: float = dataclasses.field(init=False, default=None)

    def parse(self) -> None:
        self.offset = 0
        self.result = {}
        for item, item_format in self.FORMAT.items():
            if self.length[item] != None:
                self.result[item] = np.frombuffer(self.buffer, dtype=item_format, count=self.length[item], offset=self.offset)[0]
                self.offset += self.length[item]
            elif item == 'label':
                self.result[item] = ''.join([char.decode('utf-8') for char in np.frombuffer(self.buffer, dtype=item_format, count=self.result['label_size'] * 2, offset=self.offset)])
                self.offset += self.result['label_size'] * 2
            elif item == 'unit':
                self.result[item] = ''.join([char.decode('utf-8') for char in np.frombuffer(self.buffer, dtype=item_format, count=self.result['unit_size'] * 2, offset=self.offset)])
                self.offset += self.result['unit_size'] * 2
            elif item == 'data':
                if self.result['data_size'] * 4 + self.offset > self.result['packet_len']:
                    print('Incorrect data length')
                self.result[item] = np.frombuffer(self.buffer, dtype=item_format, offset=self.offset)
        return

    def fetch_averaged_value(self, port: int) -> float:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.IP_Address, port))
        self.buffer, self.response_address = s.recvfrom(self.BUFFER_SIZE)
        s.close()
        self.parse()
        self.value = np.mean(self.result['data']) * self.result['gain']
        return self.value
