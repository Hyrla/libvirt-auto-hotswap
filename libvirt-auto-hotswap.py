#!/bin/python3

import libvirt
import pyudev
import time
from termcolor import colored
from pprint import pprint
import atexit
import settings

devices = []
conn = None

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

        self = self.add_to_list()

    def __str__(self):
        return colored(str(self.vendor), "red") + " - " + str(self.name) + " - " + colored(str(self.vendor_id) + ":" + str(self.product_id), "green") + " - " + colored("bus: " + str(self.bus_number) + "/" + str(self.device_number), "blue")

    def __eq__(self, obj):
        if not isinstance(obj, Device):
            return False
        # If the bus data are equal
        if self.device_number is not None and obj.device_number is not None and self.device_number == obj.device_number and self.bus_number == obj.bus_number:
            return True
        # If one of the devices has no name but same vendor id and product id
        if self.vendor_id is not None and self.vendor_id == obj.vendor_id and self.product_id == obj.product_id and (self.name is None or obj.name is None):
            return True
        # If one of the devices has no bus data but same vendor id and product id
        if self.vendor_id is not None and obj.vendor_id is not None and self.vendor_id == obj.vendor_id and self.product_id == obj.product_id and (self.device_number is None or obj.device_number is None):
            return True
        return False

    def add_to_list(self):
        global devices
        if not self in devices:
            devices.append(self)
            return self
        else:
            return devices[devices.index(self)]

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')
def log_event(action, device_udev):
    device = Device(device_udev)
    if action == "add":
        print("Added", device)
    elif action == "remove":
        print("Removed", device)
    else:
        print("Unkown action", action, device)
observer = pyudev.MonitorObserver(monitor, log_event)
observer.start()

def get_all_devices():
    for device in context.list_devices(subsystem="usb"):
        d = Device(device.items())
        d.add_to_list()

if __name__ == '__main__':
    get_all_devices()
    print(colored(str(len(devices)) + " USB devices connected:", "yellow"))
    for device in devices:
        print(device)

    print("\nConnecting to libvirt...")

    try:
        conn = libvirt.open(settings.hypervisor + ':///system')
    except libvirt.libvirtError:
        print(colored("Can't connect to libvirt", "red"))
        exit(1)
    atexit.register(conn.close)
    
    print("Connected to libvirt", settings.hypervisor)

    for vm in settings.vms:
        try:
            domain = conn.lookupByName(vm['domain'])
            #pprint(domain.XMLDesc(0))
        except libvirt.libvirtError:
            print(colored("Can't find domain " + vm['domain']))

    while True:
        time.sleep(2)
        pass
