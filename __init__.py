#!/usr/bin/python3
import time
from connection import ReceiveNotification
from gotway import GotwayAdapter

if __name__ == '__main__':
    euc_controller_address = 'D4:36:39:B1:7A:04'
    gotway_adapter = GotwayAdapter()
    ReceiveNotification(address=euc_controller_address, adapter=gotway_adapter)
    while True:
        time.sleep(1)
