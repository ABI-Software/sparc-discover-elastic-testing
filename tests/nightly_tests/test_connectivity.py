#===============================================================================

import unittest

#===============================================================================

from mapknowledge import KnowledgeStore, SCICRUNCH_PRODUCTION, SCICRUNCH_STAGING

#===============================================================================

from tests.config import Config

#===============================================================================

FLATMAP_MODELS = {
    'https://apinatomy.org/uris/models/keast-bladder',
    'https://apinatomy.org/uris/models/ard-arm-cardiac',
    'https://apinatomy.org/uris/models/bolser-lewis',
    'https://apinatomy.org/uris/models/bronchomotor',
    'https://apinatomy.org/uris/models/pancreas',
    'https://apinatomy.org/uris/models/sawg-distal-colon',
    'https://apinatomy.org/uris/models/sawg-stomach',
    'https://apinatomy.org/uris/models/spleen',
}

FLATMAP_MODELS_TO_NPO = {
    'https://apinatomy.org/uris/models/keast-bladder': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronKblad',
    'https://apinatomy.org/uris/models/ard-arm-cardiac': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronAacar',
    'https://apinatomy.org/uris/models/bolser-lewis': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronBolew',
    'https://apinatomy.org/uris/models/bronchomotor': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronBromo',
    'https://apinatomy.org/uris/models/pancreas': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronPancr',
    'https://apinatomy.org/uris/models/sawg-distal-colon': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronSdcol',
    'https://apinatomy.org/uris/models/sawg-stomach': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronSstom',
    'https://apinatomy.org/uris/models/spleen': 'http://uri.interlex.org/tgbugs/uris/readable/NeuronSplen',
}

APINATOMY_MODELS = {
    'SAWG_DISTAL_MODEL': {
        'id': 'https://apinatomy.org/uris/models/sawg-distal-colon',
        'label': 'https://apinatomy.org/uris/models/sawg-distal-colon',
        'paths': [
            {'id': 'ilxtr:neuron-type-sdcol-p',
                'models': 'ilxtr:neuron-type-sdcol-p'},
            {'id': 'ilxtr:neuron-type-sdcol-b',
                'models': 'ilxtr:neuron-type-sdcol-b'},
            {'id': 'ilxtr:neuron-type-sdcol-j',
                'models': 'ilxtr:neuron-type-sdcol-j'},
            {'id': 'ilxtr:neuron-type-sdcol-c',
                'models': 'ilxtr:neuron-type-sdcol-c'},
            {'id': 'ilxtr:neuron-type-sdcol-d',
                'models': 'ilxtr:neuron-type-sdcol-d'},
            {'id': 'ilxtr:neuron-type-sdcol-m',
                'models': 'ilxtr:neuron-type-sdcol-m'},
            {'id': 'ilxtr:neuron-type-sdcol-n',
                'models': 'ilxtr:neuron-type-sdcol-n'},
            {'id': 'ilxtr:neuron-type-sdcol-g',
                'models': 'ilxtr:neuron-type-sdcol-g'},
            {'id': 'ilxtr:neuron-type-sdcol-k',
                'models': 'ilxtr:neuron-type-sdcol-k'},
            {'id': 'ilxtr:neuron-type-sdcol-i',
                'models': 'ilxtr:neuron-type-sdcol-i'},
            {'id': 'ilxtr:neuron-type-sdcol-q-prime',
                'models': 'ilxtr:neuron-type-sdcol-q-prime'},
            {'id': 'ilxtr:neuron-type-sdcol-h',
                'models': 'ilxtr:neuron-type-sdcol-h'},
            {'id': 'ilxtr:neuron-type-sdcol-l',
                'models': 'ilxtr:neuron-type-sdcol-l'},
            {'id': 'ilxtr:neuron-type-sdcol-l-prime',
                'models': 'ilxtr:neuron-type-sdcol-l-prime'},
            {'id': 'ilxtr:neuron-type-sdcol-o',
                'models': 'ilxtr:neuron-type-sdcol-o'},
            {'id': 'ilxtr:neuron-type-sdcol-q',
                'models': 'ilxtr:neuron-type-sdcol-q'},
            {'id': 'ilxtr:neuron-type-sdcol-j-prime',
                'models': 'ilxtr:neuron-type-sdcol-j-prime'},
            {'id': 'ilxtr:neuron-type-sdcol-f',
                'models': 'ilxtr:neuron-type-sdcol-f'}
        ]
    },
    'ARD_ARM_CARDIAC_MODEL': {
        'id': 'https://apinatomy.org/uris/models/ard-arm-cardiac',
        'label': 'https://apinatomy.org/uris/models/ard-arm-cardiac',
        'paths': [
            {'id': 'ilxtr:neuron-type-aacar-2m',
                'models': 'ilxtr:neuron-type-aacar-2m'},
            {'id': 'ilxtr:neuron-type-aacar-4',
                'models': 'ilxtr:neuron-type-aacar-4'},
            {'id': 'ilxtr:neuron-type-aacar-9a',
                'models': 'ilxtr:neuron-type-aacar-9a'},
            {'id': 'ilxtr:neuron-type-aacar-7a',
                'models': 'ilxtr:neuron-type-aacar-7a'},
            {'id': 'ilxtr:neuron-type-aacar-2i',
                'models': 'ilxtr:neuron-type-aacar-2i'},
            {'id': 'ilxtr:neuron-type-aacar-12',
                'models': 'ilxtr:neuron-type-aacar-12'},
            {'id': 'ilxtr:neuron-type-aacar-7v',
                'models': 'ilxtr:neuron-type-aacar-7v'},
            {'id': 'ilxtr:neuron-type-aacar-5',
                'models': 'ilxtr:neuron-type-aacar-5'},
            {'id': 'ilxtr:neuron-type-aacar-8a',
                'models': 'ilxtr:neuron-type-aacar-8a'},
            {'id': 'ilxtr:neuron-type-aacar-13',
                'models': 'ilxtr:neuron-type-aacar-13'},
            {'id': 'ilxtr:neuron-type-aacar-6',
                'models': 'ilxtr:neuron-type-aacar-6'},
            {'id': 'ilxtr:neuron-type-aacar-8v',
                'models': 'ilxtr:neuron-type-aacar-8v'},
            {'id': 'ilxtr:neuron-type-aacar-9v',
                'models': 'ilxtr:neuron-type-aacar-9v'},
            {'id': 'ilxtr:neuron-type-aacar-1',
                'models': 'ilxtr:neuron-type-aacar-1'},
            {'id': 'ilxtr:neuron-type-aacar-10v',
                'models': 'ilxtr:neuron-type-aacar-10v'},
            {'id': 'ilxtr:neuron-type-aacar-11',
                'models': 'ilxtr:neuron-type-aacar-11'},
            {'id': 'ilxtr:neuron-type-aacar-10a',
                'models': 'ilxtr:neuron-type-aacar-10a'}
        ]
    },
    'BOLSER_LEWIS_MODEL': {
        'id': 'https://apinatomy.org/uris/models/bolser-lewis',
        'label': 'https://apinatomy.org/uris/models/bolser-lewis',
        'paths': [
            {'id': 'ilxtr:neuron-type-bolew-unbranched-6',
                'models': 'ilxtr:neuron-type-bolew-unbranched-6'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-8',
                'models': 'ilxtr:neuron-type-bolew-unbranched-8'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-7',
                'models': 'ilxtr:neuron-type-bolew-unbranched-7'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-9',
                'models': 'ilxtr:neuron-type-bolew-unbranched-9'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-27',
                'models': 'ilxtr:neuron-type-bolew-unbranched-27'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-4',
                'models': 'ilxtr:neuron-type-bolew-unbranched-4'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-3',
                'models': 'ilxtr:neuron-type-bolew-unbranched-3'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-1',
                'models': 'ilxtr:neuron-type-bolew-unbranched-1'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-17',
                'models': 'ilxtr:neuron-type-bolew-unbranched-17'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-10',
                'models': 'ilxtr:neuron-type-bolew-unbranched-10'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-12',
                'models': 'ilxtr:neuron-type-bolew-unbranched-12'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-11',
                'models': 'ilxtr:neuron-type-bolew-unbranched-11'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-14',
                'models': 'ilxtr:neuron-type-bolew-unbranched-14'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-13',
                'models': 'ilxtr:neuron-type-bolew-unbranched-13'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-16',
                'models': 'ilxtr:neuron-type-bolew-unbranched-16'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-15',
                'models': 'ilxtr:neuron-type-bolew-unbranched-15'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-18',
                'models': 'ilxtr:neuron-type-bolew-unbranched-18'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-19',
                'models': 'ilxtr:neuron-type-bolew-unbranched-19'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-20',
                'models': 'ilxtr:neuron-type-bolew-unbranched-20'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-22',
                'models': 'ilxtr:neuron-type-bolew-unbranched-22'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-21',
                'models': 'ilxtr:neuron-type-bolew-unbranched-21'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-28',
                'models': 'ilxtr:neuron-type-bolew-unbranched-28'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-23',
                'models': 'ilxtr:neuron-type-bolew-unbranched-23'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-25',
                'models': 'ilxtr:neuron-type-bolew-unbranched-25'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-24',
                'models': 'ilxtr:neuron-type-bolew-unbranched-24'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-29',
                'models': 'ilxtr:neuron-type-bolew-unbranched-29'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-26',
                'models': 'ilxtr:neuron-type-bolew-unbranched-26'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-5',
                'models': 'ilxtr:neuron-type-bolew-unbranched-5'},
            {'id': 'ilxtr:neuron-type-bolew-unbranched-2',
                'models': 'ilxtr:neuron-type-bolew-unbranched-2'}
        ]
    },
    'BRONCHOMOTOR_MODEL': {
        'id': 'https://apinatomy.org/uris/models/bronchomotor',
        'label': 'https://apinatomy.org/uris/models/bronchomotor',
        'paths': [
            {'id': 'ilxtr:neuron-type-bromo-3',
                'models': 'ilxtr:neuron-type-bromo-3'},
            {'id': 'ilxtr:neuron-type-bromo-4',
                'models': 'ilxtr:neuron-type-bromo-4'},
            {'id': 'ilxtr:neuron-type-bromo-5',
                'models': 'ilxtr:neuron-type-bromo-5'},
            {'id': 'ilxtr:neuron-type-bromo-6',
                'models': 'ilxtr:neuron-type-bromo-6'},
            {'id': 'ilxtr:neuron-type-bromo-2',
                'models': 'ilxtr:neuron-type-bromo-2'},
            {'id': 'ilxtr:neuron-type-bromo-1',
                'models': 'ilxtr:neuron-type-bromo-1'}
        ]
    },
    'SAWG_STOMACH': {
        'id': 'https://apinatomy.org/uris/models/sawg-stomach',
        'label': 'https://apinatomy.org/uris/models/sawg-stomach',
        'paths': [
            {'id': 'ilxtr:neuron-type-sstom-3',
                'models': 'ilxtr:neuron-type-sstom-3'},
            {'id': 'ilxtr:neuron-type-sstom-5',
                'models': 'ilxtr:neuron-type-sstom-5'},
            {'id': 'ilxtr:neuron-type-sstom-1',
                'models': 'ilxtr:neuron-type-sstom-1'},
            {'id': 'ilxtr:neuron-type-sstom-14',
                'models': 'ilxtr:neuron-type-sstom-14'},
            {'id': 'ilxtr:neuron-type-sstom-4',
                'models': 'ilxtr:neuron-type-sstom-4'},
            {'id': 'ilxtr:neuron-type-sstom-6',
                'models': 'ilxtr:neuron-type-sstom-6'},
            {'id': 'ilxtr:neuron-type-sstom-13',
                'models': 'ilxtr:neuron-type-sstom-13'},
            {'id': 'ilxtr:neuron-type-sstom-10',
                'models': 'ilxtr:neuron-type-sstom-10'},
            {'id': 'ilxtr:neuron-type-sstom-11',
                'models': 'ilxtr:neuron-type-sstom-11'},
            {'id': 'ilxtr:neuron-type-sstom-2',
                'models': 'ilxtr:neuron-type-sstom-2'},
            {'id': 'ilxtr:neuron-type-sstom-12',
                'models': 'ilxtr:neuron-type-sstom-12'},
            {'id': 'ilxtr:neuron-type-sstom-7',
                'models': 'ilxtr:neuron-type-sstom-7'},
            {'id': 'ilxtr:neuron-type-sstom-8',
                'models': 'ilxtr:neuron-type-sstom-8'},
            {'id': 'ilxtr:neuron-type-sstom-9',
                'models': 'ilxtr:neuron-type-sstom-9'}
        ]
    },
    'PANCREAS_MODEL': {
        'id': 'https://apinatomy.org/uris/models/pancreas',
        'label': 'https://apinatomy.org/uris/models/pancreas',
        'paths': [
            {'id': 'ilxtr:neuron-type-pancr-5',
                'models': 'ilxtr:neuron-type-pancr-5'},
            {'id': 'ilxtr:neuron-type-pancr-1',
                'models': 'ilxtr:neuron-type-pancr-1'},
            {'id': 'ilxtr:neuron-type-pancr-4',
                'models': 'ilxtr:neuron-type-pancr-4'},
            {'id': 'ilxtr:neuron-type-pancr-2',
                'models': 'ilxtr:neuron-type-pancr-2'},
            {'id': 'ilxtr:neuron-type-pancr-3',
                'models': 'ilxtr:neuron-type-pancr-3'}
        ]
    },
    'SPLEEN_MODEL': {
        'id': 'https://apinatomy.org/uris/models/spleen',
        'label': 'https://apinatomy.org/uris/models/spleen',
        'paths': [
            {'id': 'ilxtr:neuron-type-splen-3',
                'models': 'ilxtr:neuron-type-splen-3'},
            {'id': 'ilxtr:neuron-type-splen-2',
                'models': 'ilxtr:neuron-type-splen-2'},
            {'id': 'ilxtr:neuron-type-splen-1',
                'models': 'ilxtr:neuron-type-splen-1'},
            {'id': 'ilxtr:neuron-type-splen-4',
                'models': 'ilxtr:neuron-type-splen-4'},
            {'id': 'ilxtr:neuron-type-splen-5',
                'models': 'ilxtr:neuron-type-splen-5'}
        ]
    },
    'KEAST_BLADDER_MODEL': {
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
}

NEURON_PATHS = {
    'ilxtr:neuron-type-aacar-11': {'axons': [('UBERON:0009050', ())],
                            'connectivity': [(('UBERON:0002348',
                                                ('UBERON:0000948',)),
                                                ('UBERON:0007240',
                                                ('UBERON:0001496',))),
                                                (('UBERON:0005363', ()),
                                                ('UBERON:0002348',
                                                ('UBERON:0000948',))),
                                                (('UBERON:0002348',
                                                ('UBERON:0000948',)),
                                                ('UBERON:0002349',
                                                ('UBERON:0002079',
                                                'UBERON:0002348',
                                                'UBERON:0000948'))),
                                                (('UBERON:0002348',
                                                ('UBERON:0000948',)),
                                                ('UBERON:0007240',
                                                ('UBERON:0002012',))),
                                                (('UBERON:0002348',
                                                ('UBERON:0000948',)),
                                                ('UBERON:0002349',
                                                ('UBERON:0002078',
                                                'UBERON:0002348',
                                                'UBERON:0000948'))),
                                                (('UBERON:0001896', ()),
                                                ('UBERON:0009050',
                                                ('UBERON:0001896',))),
                                                (('UBERON:0002348',
                                                ('UBERON:0000948',)),
                                                ('UBERON:0002349',
                                                ('UBERON:0002084',
                                                'UBERON:0002348',
                                                'UBERON:0000948'))),
                                                (('UBERON:0002349',
                                                ('UBERON:0002078',
                                                'UBERON:0002348',
                                                'UBERON:0000948')),
                                                ('UBERON:0002165',
                                                ('UBERON:0002078',
                                                'UBERON:0002348',
                                                'UBERON:0000948'))),
                                                (('UBERON:0005363', ()),
                                                ('UBERON:0001896', ())),
                                                (('UBERON:0002349',
                                                ('UBERON:0002084',
                                                'UBERON:0002348',
                                                'UBERON:0000948')),
                                                ('UBERON:0002165',
                                                ('UBERON:0002084',
                                                'UBERON:0002348',
                                                'UBERON:0000948'))),
                                                (('UBERON:0002349',
                                                ('UBERON:0002079',
                                                'UBERON:0002348',
                                                'UBERON:0000948')),
                                                ('UBERON:0002165',
                                                ('UBERON:0002079',
                                                'UBERON:0002348',
                                                'UBERON:0000948')))],
                            'dendrites': [('UBERON:0007240',
                                            ('UBERON:0001496',)),
                                            ('UBERON:0002348',
                                            ('UBERON:0000948',)),
                                            ('UBERON:0002349',
                                            ('UBERON:0002078',)),
                                            ('UBERON:0002349',
                                            ('UBERON:0002079',)),
                                            ('UBERON:0002165',
                                            ('UBERON:0002084',)),
                                            ('UBERON:0002165',
                                            ('UBERON:0002078',)),
                                            ('UBERON:0002349',
                                            ('UBERON:0002084',)),
                                            ('UBERON:0007240',
                                            ('UBERON:0002012',)),
                                            ('UBERON:0002165',
                                            ('UBERON:0002079',))],
                            'errors': [],
                            'id': 'ilxtr:neuron-type-aacar-11',
                            'label': 'ilxtr:neuron-type-aacar-11',
                            'long-label': 'neuron type aacar 11',
                            'phenotypes': ['ilxtr:SensoryPhenotype'],
                            'references': ['PMID:27783854'],
                            'taxon': 'NCBITaxon:40674'},
    'ilxtr:neuron-type-bolew-unbranched-7': {'axons': [('ILX:0738371', ())],
                                        'connectivity': [(('UBERON:0006490',
                                                            ()),
                                                        ('UBERON:0006491',
                                                            ())),
                                                        (('UBERON:0006491',
                                                            ()),
                                                        ('UBERON:0006492',
                                                            ())),
                                                        (('ILX:0738320',
                                                            ('UBERON:0001896',)),
                                                        ('UBERON:0006469',
                                                            ())),
                                                        (('UBERON:0005807',
                                                            ('ILX:0738320',
                                                            'UBERON:0001896')),
                                                        ('ILX:0738320',
                                                            ('UBERON:0001896',))),
                                                        (('UBERON:0006488',
                                                            ()),
                                                        ('UBERON:0006490',
                                                            ())),
                                                        (('UBERON:0006489',
                                                            ()),
                                                        ('UBERON:0006488',
                                                            ())),
                                                        (('UBERON:0006492',
                                                            ()),
                                                        ('UBERON:0006493',
                                                            ())),
                                                        (('UBERON:0006493',
                                                            ()),
                                                        ('UBERON:0006470',
                                                            ())),
                                                        (('UBERON:0006457',
                                                            ()),
                                                        ('ILX:0738371',
                                                            ('ILX:0738306',
                                                            'UBERON:0006457'))),
                                                        (('UBERON:0006470',
                                                            ()),
                                                        ('UBERON:0006457',
                                                            ())),
                                                        (('UBERON:0006469',
                                                            ()),
                                                        ('UBERON:0006489',
                                                            ()))],
                                        'dendrites': [('UBERON:0005807', ())],
                                        'errors': [],
                                        'id': 'ilxtr:neuron-type-bolew-unbranched-7',
                                        'label': 'ilxtr:neuron-type-bolew-unbranched-7',
                                        'long-label': 'neuron type bolew '
                                                    'unbranched 7',
                                        'phenotypes': ['ilxtr:SpinalCordDescendingProjectionPhenotype'],
                                        'references': [],
                                        'taxon': 'NCBITaxon:40674'},
    'ilxtr:neuron-type-bromo-6': {'axons': [('ILX:0775392', ('UBERON:0002187',))],
                            'connectivity': [(('ILX:0793573',
                                                ('ILX:0775392',
                                                'UBERON:0002187')),
                                                ('ILX:0775392',
                                                ('UBERON:0002187',)))],
                            'dendrites': [('ILX:0793573', ())],
                            'errors': [],
                            'id': 'ilxtr:neuron-type-bromo-6',
                            'label': 'ilxtr:neuron-type-bromo-6',
                            'long-label': 'neuron type bromo 6',
                            'phenotypes': ['ilxtr:PostGanglionicPhenotype',
                                            'ilxtr:ParasympatheticPhenotype'],
                            'references': ['doi:10.1016/B978-0-444-53491-0.09985-5'],
                            'taxon': 'NCBITaxon:40674'},
    'ilxtr:neuron-type-keast-5': {'axons': [('UBERON:0016508', ())],
                            'connectivity': [(('ILX:0792853', ()),
                                                ('UBERON:0018675', ())),
                                            (('ILX:0793615', ()),
                                                ('UBERON:0018675', ())),
                                            (('UBERON:0016578',
                                                ('UBERON:0006460',)),
                                                ('UBERON:0006460', ())),
                                            (('UBERON:0016578',
                                                ('ILX:0738432',)),
                                                ('ILX:0738432', ())),
                                            (('UBERON:0018675', ()),
                                                ('UBERON:0016508', ())),
                                            (('UBERON:0006460', ()),
                                                ('ILX:0792853', ())),
                                            (('ILX:0738432', ()),
                                                ('ILX:0793615', ()))],
                            'dendrites': [('UBERON:0016578',
                                            ('UBERON:0006460',)),
                                            ('UBERON:0016578',
                                            ('ILX:0738432',))],
                            'errors': [],
                            'id': 'ilxtr:neuron-type-keast-5',
                            'label': 'parasympathetic spinal preganglionic '
                                    'neuron (kblad)',
                            'long-label': 'neuron type kblad 5',
                            'phenotypes': ['ilxtr:PreGanglionicPhenotype',
                                            'ilxtr:ParasympatheticPhenotype'],
                            'references': ['PMID:12401325',
                                            'PMID:10473279',
                                            'PMID:86176',
                                            'PMID:6736301',
                                            'PMID:7174880',
                                            'PMID:21283532',
                                            'PMID:9442414'],
                            'taxon': 'NCBITaxon:10116'},
    'ilxtr:neuron-type-pancr-4': {'axons': [('UBERON:0001263', ()),
                                        ('ILX:0793178', ())],
                            'connectivity': [(('UBERON:0001165', ()),
                                                ('UBERON:0001263', ())),
                                            (('UBERON:0001263', ()),
                                                ('ILX:0793178', ())),
                                            (('ILX:0774562', ()),
                                                ('UBERON:0001263', ())),
                                            (('UBERON:0002439',
                                                ('ILX:0774562',)),
                                                ('ILX:0774562', ())),
                                            (('UBERON:0002439',
                                                ('UBERON:0001165',)),
                                                ('UBERON:0001165', ())),
                                            (('ILX:0793178', ()),
                                                ('UBERON:0001263', ()))],
                            'dendrites': [('UBERON:0002439',
                                            ('ILX:0774562',)),
                                            ('UBERON:0002439',
                                            ('UBERON:0001165',))],
                            'errors': [],
                            'id': 'ilxtr:neuron-type-pancr-4',
                            'label': 'ilxtr:neuron-type-pancr-4',
                            'long-label': 'neuron type pancr 4',
                            'phenotypes': ['ilxtr:EntericPhenotype'],
                            'references': [],
                            'taxon': 'NCBITaxon:40674'},
    'ilxtr:neuron-type-sdcol-p': {'axons': [],
                            'connectivity': [(('ILX:0793659',
                                                ('UBERON:0001158',)),
                                                ('ILX:0770759',
                                                ('UBERON:0001158',)))],
                            'dendrites': [],
                            'errors': [],
                            'id': 'ilxtr:neuron-type-sdcol-p',
                            'label': 'ilxtr:neuron-type-sdcol-p',
                            'long-label': 'neuron type sdcol p',
                            'phenotypes': ['ilxtr:EntericPhenotype'],
                            'references': [],
                            'taxon': 'NCBITaxon:40674'},
    'ilxtr:neuron-type-splen-3': {'axons': [('UBERON:0002870', ())],
                            'connectivity': [(('UBERON:0009050',
                                                ('UBERON:0001896',)),
                                                ('UBERON:0001896', ())),
                                            (('UBERON:0001896', ()),
                                                ('UBERON:0002870',
                                                ('UBERON:0001896',)))],
                            'dendrites': [('UBERON:0009050', ())],
                            'errors': [],
                            'id': 'ilxtr:neuron-type-splen-3',
                            'label': 'ilxtr:neuron-type-splen-3',
                            'long-label': 'neuron type splen 3',
                            'phenotypes': ['ilxtr:SpinalCordDescendingProjectionPhenotype'],
                            'references': [],
                            'taxon': 'NCBITaxon:40674'},
    'ilxtr:neuron-type-sstom-6': {'axons': [],
                               'connectivity': [(('UBERON:0009050', ()),
                                                 ('UBERON:0002870', ()))],
                               'dendrites': [],
                               'errors': [],
                               'id': 'ilxtr:neuron-type-sstom-6',
                               'label': 'ilxtr:neuron-type-sstom-6',
                               'long-label': 'neuron type sstom 6',
                               'phenotypes': [],
                               'references': [],
                               'taxon': 'NCBITaxon:40674'}
}

#===============================================================================

class ConnectivityTestCase(unittest.TestCase):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        production = KnowledgeStore(
            clean_connectivity=True,
            scicrunch_api=Config.SCICRUNCH_API,
            scicrunch_key=Config.SCICRUNCH_API_KEY,
            scicrunch_release=SCICRUNCH_PRODUCTION
        )
        staging = KnowledgeStore(
            clean_connectivity=True,
            scicrunch_api=Config.SCICRUNCH_API,
            scicrunch_key=Config.SCICRUNCH_API_KEY,
            scicrunch_release=SCICRUNCH_STAGING
        )
        npo = KnowledgeStore(
            clean_connectivity=True,
            scicrunch_api=Config.SCICRUNCH_API,
            scicrunch_key=Config.SCICRUNCH_API_KEY,
            scicrunch_release=SCICRUNCH_PRODUCTION,
            npo = True
        )
        self.__stores = {
            f"SCKAN Production:{production.scicrunch.build()['released']}": production,
            f"SCKAN Staging:{staging.scicrunch.build()['released']}": staging,
            f"SCKAN Production:{npo.scicrunch.build()['released']} with NPO": npo,
        }

    def test_build(self):
        ver_production = list(self.__stores.keys())[0]
        ver_staging = list(self.__stores.keys())[1]
        released_production = self.__stores[ver_production].scicrunch.build()['released']
        released_staging = self.__stores[ver_staging].scicrunch.build()['released']
        # comparing sckan if releases are different
        if released_production != released_staging:
            connectivity_models_prod = self.__stores[ver_production].connectivity_models()
            connectivity_models_stag = self.__stores[ver_staging].connectivity_models()
            assert set(connectivity_models_prod) == set(connectivity_models_stag), \
                f"{ver_production} vs {ver_staging} - Different set of connectivity models"

    def test_ac_map_models(self):
        for version, store in self.__stores.items():
            knowledge = store.connectivity_models()
            assert len(set(FLATMAP_MODELS) - set(knowledge)) == 0, \
                f"{version} - Not all models used by FC maps are covered"
        
    def test_connectivity_neurons(self):
        for version, store in self.__stores.items():
            for model, neurons in APINATOMY_MODELS.items():
                neuron = neurons.get('id')
                if 'with NPO' in version:
                    neuron = FLATMAP_MODELS_TO_NPO[neuron]
                knowledge = store.entity_knowledge(neuron)
                assert len(knowledge)
                assert len(knowledge.get('paths', [])) == len(neurons.get('paths', [])), \
                    f"{version} - Wrong number of neuron paths for {model} model" + \
                    f"{neurons.get('id')} - {knowledge} - {version}"
                
    def test_connectivity_neuron_group(self):
        for version, store in self.__stores.items():
            for idx, path in NEURON_PATHS.items():
                knowledge = store.entity_knowledge(idx)
                assert len(knowledge)
                assert len(knowledge.get('connectivity', [])) == len(path['connectivity']), \
                    f"{version} - Incorrect number of nodes for {idx}"
                assert set(knowledge.get('axons', [])) == set(path['axons']), \
                    f"{version} - Incorrect set of axons for {idx}"
                assert set(knowledge.get('dendrites', [])) == set(path['dendrites']), \
                    f"{version} - Incorrect set of dendrites for {idx}"
                assert set(knowledge.get('phenotypes', [])) == set(path['phenotypes']), \
                    f"{version} - Incorrect set of phenotypes for {idx}"
                assert len(set(knowledge.get('references', []))) >= len(set(path['references'])), \
                    f"{version} - Too few references for {idx}"

#===============================================================================

if __name__ == '__main__':
    unittest.main()

#===============================================================================
