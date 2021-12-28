#!/bin/python3

import libvirt
import pyudev
import time
from pprint import pprint

devices = []

class Device:
    def __init__(self, device):
        if type(device) != dict:
            device = dict(device)
        self.vendor = device.get('ID_VENDOR_FROM_DATABASE', None)
        if self.vendor is None:
            self.vendor = device.get('ID_VENDOR', None)
            if self.vendor is not None:
                self.vendor = self.vendor.replace("_", " ")

        self.name = device.get('ID_MODEL_FROM_DATABASE', None)
        if self.name is None:
            self.name = device.get('ID_MODEL', None)
            if self.name is not None:
                self.name = self.name.replace("_", " ")

        self.vendor_id = device.get('ID_VENDOR_ID', None)
        self.product_id = device.get('ID_MODEL_ID', None)
        if self.vendor_id is None or self.product_id is None:
            data = device.get('PRODUCT', None)
            if data is not None:
                self.vendor_id = data.split('/')[0].zfill(4)
                self.product_id = data.split('/')[1].zfill(4)
            else:
                self.vendor_id = None
                self.product_id = None

        self.device_number = device.get('DEVNUM', None)
        self.bus_number = device.get('BUSNUM', None)

    def __str__(self):
        return str(self.vendor) + " - " + str(self.name) + " - " + str(self.vendor_id) + ":" + str(self.product_id) + " - path: " + str(self.bus_number) + "/" + str(self.device_number)

    def __eq__(self, obj):
        if not isinstance(obj, Device):
            return False
        # If the bus data are equal
        if self.device_number is not None and obj.device_number is not None and self.device_number == obj.device_number and self.bus_number == obj.bus_number:
            return True
        # If one of the devices has no name but same vendor id and product id
        if self.vendor_id == obj.vendor_id and self.product_id == obj.product_id and (self.name is None or obj.name is None):
            return True

        # If one of the devices has no bus data but same vendor id and product id
        if self.vendor_id is not None and obj.vendor_id is not None and self.vendor_id == obj.vendor_id and self.product_id == obj.product_id and (self.device_number is None or obj.device_number is None):
            return True

    def add_to_list(self):
        global devices
        if not self in devices:
            devices.append(self)

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')
def log_event(action, device):
    if action == "add":
        pprint(device.__dict__)
        print(dev.get('DEVNAME'))
observer = pyudev.MonitorObserver(monitor, log_event)
observer.start()

def test():
    for device in context.list_devices(subsystem="usb"):
        #infos = dict(device.items())
        ##print(infos.get('DEVPATH', 'Unkown path'), infos.get('DEVNAME', 'Unkown name'))
        ##print(infos)
        d = Device(device.items())
        d.add_to_list()

    for device in devices:
        print(device)

test()
#while True:
#    time.sleep(2)
#    print("Wait...")
