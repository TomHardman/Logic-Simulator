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

    G1_id, SW1_id, SW2_id, I1_id, I2_id = names.lookup(['G1', 'SW1', 'SW2', 'I1', 'I2'])
    devices.make_gate(G1_id, devices.AND, 2)
    devices.make_switch(SW1_id, 0)
    devices.make_switch(SW2_id, 1)

    network.make_connection(G1_id, I1_id, SW1_id, None)
    network.make_connection(G1_id, I2_id, SW2_id, None)

    monitor.make_monitor(G1_id, None)

    return [names, devices, network, monitor]