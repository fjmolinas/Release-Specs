import logging
import re

from iotlabcli.auth import get_user_credentials
from iotlabcli.rest import Api
from iotlabcli.experiment import (submit_experiment, wait_experiment,
                                  stop_experiment, get_experiment,
                                  exp_resources, AliasNodes)

import riotnode.node


class IOTLABNode(riotnode.node.RIOTNode):
    """Extension of RIONode that has IOTLAB_NODE and IOTLAB_EXP_ID
       to use 'flash', 'term', 'reset', etc. transparently"""
    def __init__(self, application_directory='.', env=None):
        super().__init__(application_directory, env)

    @property
    def iotlab_node(self):
        """Return IOTLAB_NODE"""
        return self.env.get('IOTLAB_NODE')

    @property
    def exp_id(self):
        """Return the IOTLAB_EXP_ID"""
        return self.env.get('IOTLAB_EXP_ID')


class IoTLABExperiment(object):
    """Utility for running iotlab-experiments based on a list of IoTLABNodes
       expects BOARD or IOTLAB_NODE variable to be set for received nodes"""
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
        IoTLABExperiment._check_site(site)
        self.site = site
        IoTLABExperiment._check_nodes(site, nodes)
        self.nodes = nodes
        self.name = name
        self.exp_id = None

    @staticmethod
    def _check_site(site):
        if site not in IoTLABExperiment.SITES:
            raise ValueError("iotlab site must be one of {}"
                             .format(IoTLABExperiment.SITES))

    @staticmethod
    def valid_board(board):
        return board in IoTLABExperiment.BOARD_ARCHI_MAP

    @staticmethod
    def valid_iotlab_node(iotlab_node, site, board=None):
        if site not in iotlab_node:
            raise ValueError("All nodes must be on the same site")
        if board is not None:
            if IoTLABExperiment._board_from_iotlab_node(iotlab_node) != board:
                raise ValueError("IOTLAB_NODE doesn't match BOARD")

    @staticmethod
    def _board_from_iotlab_node(iotlab_node):
        """Return BOARD matching iotlab_node"""
        reg = r'([0-9a-zA-Z\-]+)-\d+\.[a-z]+\.iot-lab\.info'
        match = re.search(reg, iotlab_node)
        iotlab_node_name = match.group(1)
        dict_values = IoTLABExperiment.BOARD_ARCHI_MAP.values()
        dict_names = [value['name'] for value in dict_values]
        dict_keys = list(IoTLABExperiment.BOARD_ARCHI_MAP.keys())
        return dict_keys[dict_names.index(iotlab_node_name)]

    @staticmethod
    def _archi_from_board(board):
        """Return iotlab 'archi' format for BOARD"""
        return '{}:{}'.format(IoTLABExperiment.BOARD_ARCHI_MAP[board]['name'],
                              IoTLABExperiment.BOARD_ARCHI_MAP[board]['radio'])

    @staticmethod
    def _valid_addr(node, addr):
        """Check id addr matches a specific node BOARD"""
        return addr.startswith(
            IoTLABExperiment.BOARD_ARCHI_MAP[node.board()]['name'])

    @staticmethod
    def _check_nodes(site, nodes):
        """Takes a list of nodes and validates BOARD or IOTLAB_NODE"""
        for node in nodes:
            # If BOARD is set it must be supported in iotlab
            if node.board() is not None:
                if not IoTLABExperiment.valid_board(node.board()):
                    raise ValueError("{} BOARD unsupported in iotlab")
                if node.iotlab_node is not None:
                    IoTLABExperiment.valid_iotlab_node(node.iotlab_node,
                                                       site,
                                                       node.board())
            elif node.iotlab_node is not None:
                IoTLABExperiment.valid_iotlab_node(node.iotlab_node, site)
                try:
                    board = IoTLABExperiment._board_from_iotlab_node(
                        node.iotlab_node)
                    node.env['BOARD'] = board
                except KeyError:
                    raise ValueError("Invalid IOLTAB_NODE")
            else:
                raise ValueError("BOARD or IOTLAB_NODE must be set")

    def stop(self):
        """If running stop the experiment"""
        if self.exp_id is not None:
            ret = stop_experiment(Api(*get_user_credentials()), self.exp_id)
            self.exp_id = None
            return ret

    def start(self, duration=60):
        """Submit an experiment, wait for it to be ready and map assigned
           nodes"""
        logging.info("Submitting experiment")
        self.exp_id = self._submit(site=self.site, duration=duration)
        logging.info("Waiting for experiment {} to go to state \"Running\""
                     .format(self.exp_id))
        self._wait()
        self._map_iotlab_nodes_to_RIOTNode(self._get_nodes())

    def _wait(self):
        """Wait for the experiment to finish launching"""
        ret = wait_experiment(Api(*get_user_credentials()), self.exp_id)
        return ret

    def _submit(self, site, duration):
        """Submit an experiment with required nodes"""
        api = Api(*get_user_credentials())
        resources = []
        for node in self.nodes:
            if node.iotlab_node is not None:
                resources.append(exp_resources([node.iotlab_node]))
            elif node.board() is not None:
                board = IoTLABExperiment._archi_from_board(node.board())
                alias = AliasNodes(1, site, board)
                resources.append(exp_resources(alias))
            else:
                raise ValueError("neither BOARD or IOTLAB_NODE are set")
        return submit_experiment(api, self.name, duration, resources)['id']

    def _map_iotlab_nodes_to_RIOTNode(self, iotlab_nodes):
        """Fetch reserved nodes and map each one to an IoTLABNode"""
        for node in self.nodes:
            if node.iotlab_node in iotlab_nodes:
                iotlab_nodes.remove(node.iotlab_node)
            else:
                for iotlab_node in iotlab_nodes:
                    if IoTLABExperiment._valid_addr(node, iotlab_node):
                        iotlab_nodes.remove(iotlab_node)
                        node.env['IOTLAB_NODE'] = str(iotlab_node)
            node.env['IOTLAB_EXP_ID'] = str(self.exp_id)

    def _get_nodes(self):
        """Return all nodes reserved by the experiment"""
        ret = get_experiment(Api(*get_user_credentials()), self.exp_id)
        return ret['nodes']
