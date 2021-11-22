#===============================================================================

import unittest
from urllib.parse import urljoin

#===============================================================================

import requests

#===============================================================================

from tests.config import Config

#===============================================================================

def get_connectivity(query):
    headers = {'accept': 'application/json'}
    params = {'api_key': Config.SCICRUNCH_API_KEY}
    return requests.get(urljoin(Config.SCICRUNCH_APINATOMY_HOST + '/', query),
                        headers=headers, params=params)

#===============================================================================

class ConnectivityTestCase(unittest.TestCase):

    def test_connectivity_models(self):
        response = get_connectivity('modelList.json')
        self.assertEqual(200, response.status_code)
        assert len(response.json()['nodes']) > 5

    def test_connectivity_neuron_group(self):
        neuron_group = 'ilxtr:neuron-type-keast-5'
        response = get_connectivity(f'neru-4/{neuron_group}.json')
        self.assertEqual(200, response.status_code)
        connectivity = response.json()
        self.assertGreater(len(connectivity['nodes']), 50)
        self.assertGreater(len(connectivity['edges']), 70)

#===============================================================================
