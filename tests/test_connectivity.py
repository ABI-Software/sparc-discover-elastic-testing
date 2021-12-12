#===============================================================================

import unittest
from urllib.parse import urljoin

#===============================================================================

import requests

#===============================================================================

from tests.config import Config

#===============================================================================

def get_neurons(model_id):
    # From https://github.com/SciCrunch/sparc-curation/blob/master/docs/queries.org#neru-model-populations
    # See also https://github.com/SciCrunch/sparc-curation/blob/master/docs/queries.org#neru-model-populations-and-references
    cypher = """
        MATCH (start:Ontology {{iri: "{MODEL_ID}"}})
        <-[:isDefinedBy]-(external:Class)
        -[:subClassOf*]->(:Class {{iri: "http://uri.interlex.org/tgbugs/uris/readable/NeuronEBM"}}) // FIXME
        RETURN external
    """.format(MODEL_ID=model_id)
    headers = {'accept': 'application/json'}
    params = {
        'api_key': Config.SCICRUNCH_API_KEY,
        'cypherQuery': cypher,
    }
    return requests.get(Config.SCICRUNCH_SPARC_CYPHER, headers=headers, params=params)

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

    def test_connectivity_neurons(self):
        connectivity_model = 'https://apinatomy.org/uris/models/keast-bladder'
        response = get_neurons(connectivity_model)
        self.assertEqual(200, response.status_code)
        neurons = response.json()
        self.assertEqual(len(neurons['nodes']), 20)

    def test_connectivity_neuron_group(self):
        neuron_group = 'ilxtr:neuron-type-keast-5'
        response = get_connectivity(f'neru-4/{neuron_group}.json')
        self.assertEqual(200, response.status_code)
        connectivity = response.json()
        self.assertGreater(len(connectivity['nodes']), 50)
        self.assertGreater(len(connectivity['edges']), 70)

#===============================================================================
