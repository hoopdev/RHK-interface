import socket
import numpy as np
from ctypes import *

class Listener():
    _BUFFER_SIZE = 2048
    _FORMAT = {
        'packet_len':c_uint32,
        'timestamp':c_uint64,
        'interval':c_float,
        'gain':c_float,
        'label_size':c_uint32,
        'label':c_char,
        'unit_size':c_uint32,
        'unit':c_char,
        'data_size':c_uint32,
        'data':c_int32
    }
    
    def __init__(self,ip_address):
        self.IP_Address=ip_address
        self.Length = {
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

    def parse(self):
        self.offset = 0
        self.result={}
        for item,item_format in self._FORMAT.items():
            if self.Length[item] != None:
                self.result[item] = np.frombuffer(self.buffer, dtype=item_format, count=self.Length[item], offset=self.offset)[0]
                self.offset += self.Length[item]
            elif item == 'label':
                self.result[item] = ''.join([char.decode('utf-8') for char in np.frombuffer(self.buffer, dtype=item_format, count=self.result['label_size']*2, offset=self.offset)])
                self.offset += self.result['label_size']*2
            elif item == 'unit':
                self.result[item] = ''.join([char.decode('utf-8') for char in np.frombuffer(self.buffer, dtype=item_format, count=self.result['unit_size']*2, offset=self.offset)])
                self.offset += self.result['unit_size']*2
            elif item == 'data':
                if self.result['data_size']*4+self.offset > self.result['packet_len']:
                    print('Incorrect data length')
                self.result[item] = np.frombuffer(self.buffer, dtype=item_format, offset=self.offset)

    def fetch_averaged_value(self,port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.IP_Address, port))
        self.buffer, address = s.recvfrom(self._BUFFER_SIZE)
        s.close()
        self.parse()
        return np.mean(self.result['data'])*self.result['gain']