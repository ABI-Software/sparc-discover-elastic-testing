#===============================================================================

import unittest
from urllib.parse import urljoin

#===============================================================================

import requests

#===============================================================================

from mapknowledge import KnowledgeStore

#===============================================================================

from tests.config import Config

#===============================================================================

KEAST_BLADDER_MODEL = {
    'id': 'https://apinatomy.org/uris/models/keast-bladder',
    'label': 'https://apinatomy.org/uris/models/keast-bladder',
    'paths': [
        {'id': 'ilxtr:neuron-type-keast-13',
         'models': 'ilxtr:neuron-type-keast-13'},
        {'id': 'ilxtr:neuron-type-keast-2',
         'models': 'ilxtr:neuron-type-keast-2'},
        {'id': 'ilxtr:neuron-type-keast-20',
         'models': 'ilxtr:neuron-type-keast-20'},
        {'id': 'ilxtr:neuron-type-keast-3',
         'models': 'ilxtr:neuron-type-keast-3'},
        {'id': 'ilxtr:neuron-type-keast-16',
         'models': 'ilxtr:neuron-type-keast-16'},
        {'id': 'ilxtr:neuron-type-keast-1',
         'models': 'ilxtr:neuron-type-keast-1'},
        {'id': 'ilxtr:neuron-type-keast-8',
         'models': 'ilxtr:neuron-type-keast-8'},
        {'id': 'ilxtr:neuron-type-keast-7',
         'models': 'ilxtr:neuron-type-keast-7'},
        {'id': 'ilxtr:neuron-type-keast-12',
         'models': 'ilxtr:neuron-type-keast-12'},
        {'id': 'ilxtr:neuron-type-keast-10',
         'models': 'ilxtr:neuron-type-keast-10'},
        {'id': 'ilxtr:neuron-type-keast-11',
         'models': 'ilxtr:neuron-type-keast-11'},
        {'id': 'ilxtr:neuron-type-keast-4',
         'models': 'ilxtr:neuron-type-keast-4'},
        {'id': 'ilxtr:neuron-type-keast-17',
         'models': 'ilxtr:neuron-type-keast-17'},
        {'id': 'ilxtr:neuron-type-keast-5',
         'models': 'ilxtr:neuron-type-keast-5'},
        {'id': 'ilxtr:neuron-type-keast-9',
         'models': 'ilxtr:neuron-type-keast-9'},
        {'id': 'ilxtr:neuron-type-keast-18',
         'models': 'ilxtr:neuron-type-keast-18'},
        {'id': 'ilxtr:neuron-type-keast-6',
         'models': 'ilxtr:neuron-type-keast-6'},
        {'id': 'ilxtr:neuron-type-keast-19',
         'models': 'ilxtr:neuron-type-keast-19'},
        {'id': 'ilxtr:neuron-type-keast-15',
         'models': 'ilxtr:neuron-type-keast-15'},
        {'id': 'ilxtr:neuron-type-keast-14',
         'models': 'ilxtr:neuron-type-keast-14'}
    ]
}

KEAST_NEURON_PATH_5 = {
    'id': 'ilxtr:neuron-type-keast-5',
    'label': 'parasympathetic spinal preganglionic neuron (kblad)',
    'long-label': 'neuron type kblad 5',
    'phenotypes': [
        'ilxtr:ParasympatheticPhenotype',
        'ilxtr:PreGanglionicPhenotype'
    ],
    'axons': [
        ('UBERON:0016508', ())
    ],
    'dendrites': [
        ('UBERON:0016578', ('UBERON:0006460',)),
        ('UBERON:0016578', ('ILX:0738432',))
    ],
    'connectivity': [
        (('ILX:0793615', ()), ('UBERON:0018675', ())),
        (('UBERON:0016578', ('ILX:0738432',)), ('ILX:0738432', ())),
        (('UBERON:0018675', ()), ('UBERON:0016508', ())),
        (('UBERON:0016578', ('UBERON:0006460',)), ('UBERON:0006460', ())),
        (('UBERON:0006460', ()), ('ILX:0792853', ())),
        (('ILX:0792853', ()), ('UBERON:0018675', ())),
        (('ILX:0738432', ()), ('ILX:0793615', ()))
    ],
    'references': [
        'PMID:10473279',
        'PMID:86176',
        'PMID:7174880',
        'PMID:21283532',
        'PMID:12401325',
        'PMID:6736301',
        'PMID:9442414'
    ],
    'errors': []
}

#===============================================================================

class ConnectivityTestCase(unittest.TestCase):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__knowledge_store = KnowledgeStore(
            clean_connectivity=True,
            scicrunch_api=Config.SCICRUNCH_API,
            scicrunch_key=Config.SCICRUNCH_API_KEY
        )

    def test_connectivity_neurons(self):
        knowledge = self.__knowledge_store.entity_knowledge(KEAST_BLADDER_MODEL['id'])
        assert len(knowledge)
        assert len(knowledge.get('paths')) == 20, 'Wrong number of neuron paths for Keast bladder model'

    def test_connectivity_neuron_group(self):
        knowledge = self.__knowledge_store.entity_knowledge(KEAST_NEURON_PATH_5['id'])
        assert len(knowledge)
        assert len(knowledge.get('connectivity', [])) == len(KEAST_NEURON_PATH_5['connectivity']), 'Incorrect number of nodes for Keast neuron path 5'
        assert set(knowledge.get('axons', [])) == set(KEAST_NEURON_PATH_5['axons']), 'Incorrect set of axons for Keast neuron path 5'
        assert set(knowledge.get('dendrites', [])) == set(KEAST_NEURON_PATH_5['dendrites']), 'Incorrect set of dendrites for Keast neuron path 5'
        assert set(knowledge.get('phenotypes', [])) == set(KEAST_NEURON_PATH_5['phenotypes']), 'Incorrect phenotypes for Keast neuron path 5'
        assert len(knowledge.get('references', [])) > 5, 'Too few references for Keast neuron path 5'

#===============================================================================
