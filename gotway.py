#!/usr/bin/python3
import sys
import ctypes
import struct
from threading import Event
from bluetooth.ble import GATTRequester
from bluetooth.ble import BTIOException

gotway_adapter = None


class GotwayAdapter(object):
    RATIO_GW = 0.875
    WHEEL_VOLTAGE = 84

    def parse_data(self, data):
        buff_idx_offset = 3
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
                    # Voltage formula don't work how it is expected
                    # voltage = raw_voltage * (1 + (0.25 * self.WHEEL_VOLTAGE))
                    voltage_adjust = 79.6
                    voltage = round(raw_voltage / voltage_adjust, 2)

                    raw_speed = ((buff[4 + buff_idx_offset] << 8) | (buff[5 + buff_idx_offset] & 0xFF))
                    float_speed = raw_speed
                    if float_speed >> 12 == 0xF:
                        float_speed = (~float_speed & 0xFFFF) + 1
                    speed = round(3.6 * float_speed * self.RATIO_GW / 100, 2)

                    raw_distance = 0
                    distance = raw_distance

                    raw_current = 0
                    current = raw_current

                    raw_temperature = ((buff[12 + buff_idx_offset] << 8) | (buff[13 + buff_idx_offset] & 0xFF))
                    temperature_adjust = 36.53
                    temperature = round((raw_temperature / 340 + temperature_adjust), 2)

                    print(f'Voltage: {voltage}; Speed: {speed}; Distance: {distance}; Current: {current}; Temperature: {temperature};')
                elif buff[18 + buff_idx_offset] == 0x04 or buff[18 + buff_idx_offset] == 0x4:
                    print(f'len {buff_len} Frame B data', ' '.join(buff_str[buff_idx_offset:]))
                else:
                    print(f'len {buff_len} Frame N data', ' '.join(buff_str[buff_idx_offset:]), 'Unknown 18:', buff_str[18 + buff_idx_offset])


class Requester(GATTRequester):
    def __init__(self, wakeup, *args):
        GATTRequester.__init__(self, *args)
        self.wakeup = wakeup

    def on_notification(self, data, *args, **kwargs):
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

    def connect(self, *args, **kwargs):
        print('Connecting...', end=' ')
        sys.stdout.flush()

        self.requester.connect(True, *args, **kwargs)
        print('OK!')

    def wait_notification(self):
        print('\nThis is a bit tricky. You need to make your device to send\nsome notification. I\'ll wait...')
        self.received.wait()
