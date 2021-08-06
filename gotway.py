#!/usr/bin/python3
import ctypes
import struct


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
