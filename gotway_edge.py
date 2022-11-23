#!/usr/bin/python3
import sys
import time
import ctypes
import struct
from threading import Event
from bluetooth.ble import GATTRequester
from bluetooth.ble import BTIOException

#
# https://pybluez.readthedocs.io/en/latest/
# https://github.com/pybluez/pybluez
# https://github.com/oscaracena/pygattlib#python-pip
# sudo apt install pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev python-dev
#
# https://gist.github.com/b1oki/b6abbdc497faf89f90cc764dd9b94c3c

gotway_adapter = None


class GotwayAdapter(object):
    RATIO_GW = 0.875
    WHEEL_VOLTAGE = 84

    def parse_data(self, data):
        #from debugging import breakpoint
        #breakpoint()
        buff_idx_offset = 3
        # print('bytes received:', end=' ')
        buff = []
        buff_str = []
        for b in data:
            buff.append(b)
            buff_str.append(hex(b))
        buff_len = len(buff)
        print(f'len {buff_len} data', ' '.join(buff_str))
        if buff_len >= 18 + buff_idx_offset:
            if buff[0 + buff_idx_offset] == 0x55 and buff[1 + buff_idx_offset] == 0xAA:
                if buff[18 + buff_idx_offset] == 0x0:
                    print(f'len {buff_len} Frame A data', ' '.join(buff_str[buff_idx_offset:]))

                    raw_voltage = (((buff[2 + buff_idx_offset] & 0xFF) << 8) | (buff[3 + buff_idx_offset] & 0xFF))
                    # print(f'raw voltage {raw_voltage}')
                    # voltage = raw_voltage * (1 + (0.25 * self.WHEEL_VOLTAGE))
                    # print(f'voltage {voltage}')
                    voltage = round(raw_voltage / 79.6, 2)
                    print(f'voltage {voltage}')

                    raw_speed = ((buff[4 + buff_idx_offset] << 8) | (buff[5 + buff_idx_offset] & 0xFF))
                    # print(f'raw speed {raw_speed}')
                    if raw_speed >> 12 == 0xF:
                        raw_speed = (~raw_speed & 0xFFFF) + 1
                    speed = 3.6 * raw_speed * self.RATIO_GW / 100
                    speed = round(speed, 2)
                    print(f'speed {speed}')

                    raw_distance = 0

                    raw_current = 0

                    raw_temperature = ((buff[12 + buff_idx_offset] << 8) | (buff[13 + buff_idx_offset] & 0xFF))
                    # print(f'raw temperature {raw_temperature}')
                    temperature = (raw_temperature / 340 + 36.53)
                    temperature = round(temperature, 2)
                    print(f'temperature {temperature}')

                elif buff[18 + buff_idx_offset] == 0x04 or buff[18 + buff_idx_offset] == 0x4:
                    print(f'len {buff_len} Frame B data', ' '.join(buff_str[buff_idx_offset:]))
                else:
                    print(f'len {buff_len} Frame N data', ' '.join(buff_str[buff_idx_offset:]), 'Unknown 18:', buff_str[18 + buff_idx_offset])


class Requester(GATTRequester):
    def __init__(self, wakeup, *args):
        GATTRequester.__init__(self, *args)
        self.wakeup = wakeup

    def on_notification(self, handle, data):
        # print(f'- notification on handle: {handle}\n')
        gotway_adapter.parse_data(data)
        self.wakeup.set()


class ReceiveNotification(object):
    def __init__(self, address):
        self.received = Event()
        try:
            self.requester = Requester(self.received, address, False)
            self.connect()
        except BTIOException as error:
            print(f'Connect to {address} failed')
            print(error)
            exit(-1)
        self.wait_notification()

    def connect(self):
        print('Connecting...', end=' ')
        sys.stdout.flush()

        self.requester.connect(True)
        print('OK!')

    def wait_notification(self):
        print('\nThis is a bit tricky. You need to make your device to send\nsome notification. I\'ll wait...')
        self.received.wait()


if __name__ == '__main__':
    euc_controller_address = 'D4:36:39:B1:7A:04'
    timer = 60
    gotway_adapter = GotwayAdapter()
    ReceiveNotification(address=euc_controller_address)
    time.sleep(timer)
    print('Done.')
