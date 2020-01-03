import os
import logging

from iotlabcli.auth import get_user_credentials
from iotlabcli.rest import Api
from iotlabcli.experiment import (submit_experiment, wait_experiment,
                                  stop_experiment, get_experiment,
                                  exp_resources, AliasNodes)

import riotnode.node


class IOTLABNode(riotnode.node.RIOTNode):
    """Extension of RIONode that has IOTLAB_NODE and IOTLAB_EXP_ID
       to use 'flash', 'term', 'reset', ec. transparently"""
    def __init__(self, application_directory='.', env=None):
        super().__init__(application_directory, env)

    @property
    def iotlab_node(self):
        """Return the IOTLAB_NODE"""
        return self.env['IOTLAB_NODE']

    @property
    def exp_id(self):
        """Return the IOTLAB_EXP_ID"""
        return self.env['IOTLAB_EXP_ID']


class IoTLABExperiment(object):
    """Utility for running iotlab-experiments base on a list on IoTLABNodes"""

    BOARD_ARCHI_MAP = {
        'arduino-zero': {'name': 'arduino-zero', 'radio': 'xbee'},
        'b-l072z-lrwan1': {'name': 'st-lrwan1', 'radio': 'sx1276'},
        'b-l475e-iot01a': {'name': 'st-iotnode', 'radio': 'multi'},
        'firefly': {'name': 'firefly'},
        'frdm-kw41z': {'name': 'frdm-kw41z', 'radio': 'multi'},
        'iotlab-a8-m3': {'name': 'a8', 'radio': 'at86rf231'},
        'iotlab-m3': {'name': 'm3', 'radio': 'at86rf231'},
        'microbit': {'name': 'microbit', 'radio': 'ble'},
        'nrf51dk': {'name': 'nrf51dk', 'radio': 'ble'},
        'nrf52dk': {'name': 'nrf52dk', 'radio': 'ble'},
        'nrf52832-mdk': {'name': 'nrf52832mdk', 'radio': 'ble'},
        'nrf52840dk': {'name': 'nrf52840dk', 'radio': 'multi'},
        'nrf52840-mdk': {'name': 'nrf52840mdk', 'radio': 'multi'},
        'pba-d-01-kw2x': {'name': 'phynode', 'radio': 'kw2xrf'},
        'samr21-xpro': {'name': 'samr21', 'radio': 'at86rf233'},
        'samr30-xpro': {'name': 'samr30', 'radio': 'at86rf212b'},
        'wsn430-v1_3b': {'name': 'wsn430', 'radio': 'cc1101'},
        'wsn430-v1_4': {'name': 'wsn430', 'radio': 'cc2420'},
    }

    SITES = ['grenoble', 'lille', 'saclay']

    def __init__(self, name, nodes, site='saclay'):
        assert(site in IoTLABExperiment.SITES)
        self.nodes = nodes
        self.name = name
        self.site = site
        self.exp_id = None


    def stop(self):
        """If running stop the experiment"""
        if self.exp_id is not None:
            ret = stop_experiment(Api(*get_user_credentials()), self.exp_id)
            self.exp_id = None
            return ret

    def start(self, duration=60):
        """Submit an experiment, wait for it to be ready and map assigned
           nodes """
        logging.info("Submitting experiment")
        self.exp_id = self._submit(site=self.site, duration=duration)
        logging.info("Waiting for experiment {} to go to state \"Running\""
                    .format(self.exp_id))
        self._wait()
        self._map_iotlab_nodes_to_RIOTNode()

    def _wait(self):
        """Wait for the experiment to finish launching"""
        ret = wait_experiment(Api(*get_user_credentials()), self.exp_id)
        return ret

    def _submit(self, site='saclay', duration=60):
        """Submit an experiment with required nodes"""
        boards = [node.board() for node in self.nodes]
        api  = Api(*get_user_credentials())
        resources = []
        for board in boards:
            alias = AliasNodes(1, site, self._iotlab_archi(board))
            resources.append(exp_resources(alias))
        return submit_experiment(api, self.name, duration, resources)['id']


    def _map_iotlab_nodes_to_RIOTNode(self):
        """Fetches nodes reserved by an experiment maps one to each IoTLABNode"""
        addr_list = self._get_nodes()
        for node in self.nodes:
            addr = next(a for a in addr_list if self._valid_addr(node, a))
            node.env['IOTLAB_EXP_ID'] = str(self.exp_id)
            node.env['IOTLAB_NODE'] = str(addr)
            addr_list.remove(addr)

    def _get_nodes(self):
        """Return all nodes for the experiment"""
        ret = get_experiment(Api(*get_user_credentials()), self.exp_id)
        return ret['nodes']

    def _iotlab_archi(self, board):
        """Return iotlab 'archi' format for BOARD"""
        return '{}:{}'.format(IoTLABExperiment.BOARD_ARCHI_MAP[board]['name'], 
                              IoTLABExperiment.BOARD_ARCHI_MAP[board]['radio'])
    
    def _valid_addr(self, node, addr):
        """Check id addr matches a specific node BOARD"""
        return addr.startswith(
            IoTLABExperiment.BOARD_ARCHI_MAP[node.board()]['name'])