#!/usr/bin/python3
import time
import gotway

if __name__ == '__main__':
    timer = 60
    euc_controller_address = 'D4:36:39:B1:7A:04'
    gotway_adapter = gotway.GotwayAdapter()
    gotway.ReceiveNotification(address=euc_controller_address)
    time.sleep(timer)
    print('Done.')
