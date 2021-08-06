#!/usr/bin/python3
import sys
from threading import Event
from bluetooth.ble import GATTRequester
from bluetooth.ble import BTIOException


class Requester(GATTRequester):
    adapter = None

    def __init__(self, adapter, wakeup, *args, **kwargs):
        GATTRequester.__init__(self, *args, **kwargs)
        self.adapter = adapter
        self.wakeup = wakeup

    def on_notification(self, *args, **kwargs):
        self.adapter.parse_data(*args, **kwargs)
        self.wakeup.set()


class ReceiveNotification(object):
    def __init__(self, address, adapter):
        self.received = Event()
        try:
            self.requester = Requester(adapter, self.received, address, False)
            self.connect()
        except BTIOException as error:
            print(f'Connect to {address} failed: {error}')
            exit(-1)
        self.wait_notification()

    def connect(self, *args, **kwargs):
        print('Connecting...')
        sys.stdout.flush()
        self.requester.connect(True, *args, **kwargs)
        print('OK!')

    def wait_notification(self):
        print('This is a bit tricky. You need to make your device to send some notification. I will wait...')
        self.received.wait()
