import json
import unittest
import requests

from algoliasearch.search_client import SearchClient

from urllib.parse import urljoin

from tests.config import Config

SCICRUNCH_DOI_AGGREGATION = {
    "from": 0,
    "size": 0,
    "aggregations": {
        "doi": {
            "composite": {
                "size": 1000,
                "sources": [
                    {
                        "curie": {"terms": {"field": "item.curie.aggregate"}}
                    }
                ],
                "after": {"curie": ""}
            }
        }
    }
}

def checkResult(client, result1, result2, name_doi_map, name):
    not_found_doi = []
    for test_doi in result1:
        if f'doi:{test_doi}' not in result2:
            not_found_doi.append(test_doi)

    if len(not_found_doi):
        print(f"{name}: Not found datasets report:")
    for doi in not_found_doi:
        print(f"  {name_doi_map[doi]['id']} - {doi} - {name_doi_map[doi]['name']}")

    # Can everything in discover be found on SciCrunch?
    client.assertEqual([], not_found_doi, name)


class ComparisonTestCase(unittest.TestCase):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__scicrunch_doi = []
        headers = {'accept': 'application/json'}
        params = {'api_key': Config.SCICRUNCH_API_KEY}

        scicrunch_host = Config.SCICRUNCH_API_HOST + '/'

        scicrunch_response = requests.post(urljoin(scicrunch_host, '_search'), json=SCICRUNCH_DOI_AGGREGATION, params=params, headers=headers)
        self.assertEqual(200, scicrunch_response.status_code)

        json_data = scicrunch_response.json()
        aggregations = json_data['aggregations']
        buckets = aggregations['doi']['buckets']
        for bucket in buckets:
            self.__scicrunch_doi.append(bucket['key']['curie'])

    def test_doi_information(self):
        pennsieve_host = Config.PENNSIEVE_API_HOST + '/'

        scicrunch_doi = self.__scicrunch_doi

        headers = {'accept': 'application/json'}
        params = {'limit': 0, 'embargo': False}
        find_total_response = requests.get(urljoin(pennsieve_host, 'datasets'), params=params, headers=headers)
        self.assertEqual(200, find_total_response.status_code)

        test_response = requests.get(urljoin(pennsieve_host, f'organizations/{Config.SPARC_PENNSIEVE_ORGANISATION_ID}/datasets/metrics'), headers=headers)
        json_data = test_response.json()
        datasets = json_data['datasets']
        sparc_dataset_ids = []
        for dataset in datasets:
            sparc_dataset_ids.append(dataset['id'])

        json_data = find_total_response.json()
        total_count = json_data['totalCount']
        params = {'limit': total_count, 'embargo': False}
        response = requests.get(urljoin(pennsieve_host, 'datasets'), params=params, headers=headers)
        self.assertEqual(200, response.status_code)

        json_data = json.loads(response.text)
        discover_doi = []
        name_doi_map = {}
        for dataset in json_data['datasets']:
            if dataset['id'] in sparc_dataset_ids:
                discover_doi.append(dataset['doi'])
                name_doi_map[dataset['doi']] = {'name': dataset['name'], 'id': dataset['id']}
        # self.assertEqual(total_count, len(discover_doi))

        checkResult(self, discover_doi, scicrunch_doi, name_doi_map, 'Pennsieve vs SciCrunch')


    def test_aloglia_information(self):
        scicrunch_doi = self.__scicrunch_doi

        client = SearchClient.create(Config.ALGOLIA_ID, Config.ALGOLIA_KEY)
        index = client.init_index(Config.ALGOLIA_INDEX)

        res = index.search('', {
            'attributesToRetrieve': [
                'item.curie',
                'item.name'
            ],
            'attributesToHighlight': [],
            'length': 1000,
            'offset': 0
        })

        self.assertFalse('status' in res)
        self.assertTrue('hits' in res)

        client.close()

        algolia_doi = []
        name_doi_map = {}
        for item in res['hits']:
            doi = item['item']['curie'].replace('DOI:', '', 1)
            algolia_doi.append(doi)
            name_doi_map[doi] = {'name': item['item']['name'], 'id': item['objectID']}

        checkResult(self, algolia_doi, scicrunch_doi, name_doi_map, 'Algolia vs SciCrunch')


if __name__ == '__main__':
    unittest.main()
