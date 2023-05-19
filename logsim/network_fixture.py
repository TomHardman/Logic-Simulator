from network import Network
from devices import Devices
from monitors import Monitors
from names import Names


def create_network_fixture():
    """Creates a network fixture of 1 AND gate and 6 switches"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitor = Monitors(names, devices, network)

    G1_id,G2_id, SW1_id, SW2_id, SW3_id, SW4_id, SW5_id, SW6_id, I1_id, I2_id = names.lookup(['G1','G2', 'SW1', 'SW2',
                                                                                        'SW3', 'SW4', 'SW5', 'SW6',
                                                                                        'I1', 'I2'])
    devices.make_gate(G1_id, devices.AND, 2)
    devices.make_gate(G2_id, devices.AND, 2)
    network.make_connection(G1_id, None, G2_id, I1_id)

    devices.make_switch(SW1_id, 0)
    devices.make_switch(SW2_id, 0)
    devices.make_switch(SW3_id, 1)
    devices.make_switch(SW4_id, 0)
    devices.make_switch(SW5_id, 1)
    devices.make_switch(SW6_id, 0)

    # network.make_connection(G1_id, I1_id, SW1_id, None)
    # network.make_connection(G1_id, I2_id, SW2_id, None)
    # network.make_connection(G1_id, I1_id, SW3_id, None)
    # network.make_connection(G1_id, I2_id, SW4_id, None)
    # network.make_connection(G1_id, I1_id, SW5_id, None)
    # network.make_connection(G1_id, I2_id, SW6_id, None)

    monitor.make_monitor(G1_id, None)

    return [names, devices, network, monitor]