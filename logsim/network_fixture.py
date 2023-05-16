from network import Network
from devices import Devices
from monitors import Monitors
from names import Names

def create_network_fixture():
    """Creates a network fixture of 1 AND gate and 2 switches"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitor = Monitors(names, devices, network)

    devices.make_gate(0, "AND", 2)
    devices.make_switch(1, 0)
    devices.make_switch(2, 1)

    network.make_connection(0,names.lookup("I1"), 1, None)
    network.make_connection(0,names.lookup("I2"), 2, None)

    monitor.make_monitor(0, None)

    return [names, devices, network, monitor]