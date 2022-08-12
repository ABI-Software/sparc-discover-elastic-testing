import unittest
import requests
import botocore
import boto3
import json
import urllib.parse

from urllib.parse import urljoin

from tests.config import Config

error_report = {}

s3 = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_KEY,
    aws_secret_access_key=Config.AWS_SECRET,
    region_name="us-east-1",
)

S3_BUCKET_NAME = "pennsieve-prod-discover-publish-use1"

CONTEXT_FILE = 'abi-context-file'
PLOT_FILE = 'abi-plot'
SCAFFOLD_FILE = 'abi-scaffold-metadata-file'
SCAFFOLD_VIEW_FILE = 'abi-scaffold-view-file'
THUMBNAIL_IMAGE = 'abi-thumbnail'
NOT_SPECIFIED = 'not-specified'

TEST_MIME_TYPES = {
    'application/x.vnd.abi.context-information+json': CONTEXT_FILE,
    'application/x.vnd.abi.scaffold.meta+json': SCAFFOLD_FILE,
    'application/x.vnd.abi.scaffold.view+json': SCAFFOLD_VIEW_FILE,
    'image/x.vnd.abi.thumbnail+jpeg': THUMBNAIL_IMAGE,
    'inode/vnd.abi.scaffold+file': SCAFFOLD_FILE,
    'inode/vnd.abi.scaffold+thumbnail': THUMBNAIL_IMAGE,
    'inode/vnd.abi.scaffold.thumbnail+file': THUMBNAIL_IMAGE,
    "text/vnd.abi.plot+thumbnail": THUMBNAIL_IMAGE,
    "inode/vnd.abi.plot+thumbnail": THUMBNAIL_IMAGE,
    'inode/vnd.abi.scaffold.view+file': SCAFFOLD_VIEW_FILE,
    'text/vnd.abi.plot+tab-separated-values': PLOT_FILE,
    'text/vnd.abi.plot+csv': PLOT_FILE
}

def getDatasets(start, size):

    headers = {'accept': 'application/json'}
    params = {'api_key': Config.SCICRUNCH_API_KEY}

    scicrunch_host = Config.SCICRUNCH_API_HOST + '/'

    scicrunch_request = {
        "from": start,
        "size": size,
        "_source": [
            "item.name",
            "item.curie",
            "objects.datacite",
            "objects.additional_mimetype",
            "objects.dataset",
            "pennsieve.version",
            "pennsieve.identifier"
        ]
    }

    return requests.post(urljoin(scicrunch_host, '_search?preference=abiknowledgetesting'), json=scicrunch_request, params=params, headers=headers)

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

def map_mime_type(mime_type, obj):
    if mime_type == '':
        return NOT_SPECIFIED

    if mime_type == NOT_SPECIFIED:
        return NOT_SPECIFIED

    lower_mime_type = mime_type.lower()

    if lower_mime_type in TEST_MIME_TYPES:
        return TEST_MIME_TYPES[lower_mime_type]

    return NOT_SPECIFIED

def getFileResponse(path, mime_type):
    try:
        head_response = s3.head_object(
            Bucket=S3_BUCKET_NAME,
            Key=path,
            RequestPayer="requester"
        )
        if head_response and 'ResponseMetadata' in head_response \
            and 200 == head_response['ResponseMetadata']['HTTPStatusCode']:
            pass
        else:
            return {
                'mime_type': mime_type,
                'path': path,
                'reason': 'Invalid response'
            }
    except botocore.exceptions.ClientError as error:
        return {
            'mime_type': mime_type,
            'path': path,
            'reason': f"{error}"
        }
    return None

def getDataciteReport(obj_list, obj, mapped_mimetype, filePath):
    reports = {'TotalErrors':0, 'ItemTested':0, 'IsDerived': []}

    if 'datacite' in obj:
        if 'isDerivedFrom' in obj['datacite']:
            isDerivedFrom = obj['datacite']['isDerivedFrom']
            if 'relative' in isDerivedFrom and 'path' in isDerivedFrom['relative']:
                for path in isDerivedFrom['relative']['path']:
                    reports['ItemTested'] +=1
                    try:
                        actualPath = urllib.parse.urljoin(filePath, path)
                        found = next((i for i, item in enumerate(obj_list) if item['dataset']['path'] == actualPath), None)
                        if found == None:
                            reports['IsDerived'].append(
                                {
                                    'relativePath': path,     
                                    'reason': 'Cannot found the path'
                                }
                            )
                            reports['TotalErrors'] +=1
                    except:
                        reports['IsDerived'].append(
                            {
                                'relativePath': path,
                                'reason': 'Encounter a problem while looking for path'
                            }
                        )
                        reports['TotalErrors'] +=1

    return reports


def testObj(obj_list, obj, mime_type, prefix):
    dataciteReport = None
    fileResponse = None

    if 'dataset' in obj and 'path' in obj['dataset']:
        localPath = obj['dataset']['path']
        path = f"{prefix}/{localPath}"
        fileResponse = getFileResponse(path, mime_type)
        dataciteReport = getDataciteReport(obj_list, obj, mime_type, localPath)
        if dataciteReport['TotalErrors'] > 0:
            if fileResponse == None:
                fileResponse = {
                    'mime_type': mime_type,
                    'path': localPath,
                }
            fileResponse['dataciteReport'] = dataciteReport
    else:
        fileResponse = {
            'mime_type': mime_type,
            'path': 'Not found',
            'reason': "Cannot find path"
        }
        
    return fileResponse

def test_obj_list(id, version, obj_list):
    objectErrors = []
    prefix = f"{id}/{version}/files"
    for obj in obj_list:
        mime_type = obj.get('additional_mimetype', NOT_SPECIFIED)
        if mime_type != NOT_SPECIFIED:
            mime_type = mime_type.get('name')
        mapped_mime_type = map_mime_type(mime_type, obj)
        if mapped_mime_type == NOT_SPECIFIED:
            pass
        else:
            error = testObj(obj_list, obj, mime_type, prefix)
            if error:
                objectErrors.append(error)

    numberOfErrors = len(objectErrors)
    fileReports = {
        'Total': numberOfErrors,
        'Objects': objectErrors
    }
    return fileReports
                

def test_datasets_information(client, dataset):
    report = {
        'Id': 'none',
        'DOI': 'none',
        '_id': dataset['_id'],
        'Errors': [],
        'ObjectErrors': {'Total': 0, 'Objects':[]}
    }
    if '_source' in dataset :
        source = dataset['_source']
        if 'item' in source:
            report['Name'] = source['item'].get('name', 'none')
            report['DOI'] = source['item'].get('curie', 'none')
        if 'pennsieve' in source and 'version' in source['pennsieve'] and 'identifier' in source['pennsieve']:
            id = source['pennsieve']['identifier']
            version = source['pennsieve']['version']['identifier']
            report['Id'] = id
            if version:
                if 'objects' in source:
                    obj_list = source['objects']
                    fileReports = test_obj_list(id, version, obj_list)
                    report['ObjectErrors'] = fileReports
            else:
                report['Errors'].append('Missing version')
    return report


class SciCrunchDatasetFilesTest(unittest.TestCase):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def test_files_information(self):
        start = 0
        size = 20
        keepGoing = True
        totalSize = 0
        reports = {'Tested': 0, 'Failed': 0, 'FailedIds':[], 'Datasets':[]}
        while keepGoing:
            scicrunch_response = getDatasets(start, size)
            self.assertEqual(200, scicrunch_response.status_code)

            data = scicrunch_response.json()

            if size > len(data['hits']['hits']):
                keepGoing = False

            start = start + size
         
            for dataset in data['hits']['hits']:
                report = test_datasets_information(self, dataset)
                print(f"Reports generated for {report['Id']}")
                if len(report['Errors']) > 0 or report['ObjectErrors']['Total'] > 0:
                    reports['FailedIds'].append(report['Id'])
                    reports['Datasets'].append(report)

            totalSize = totalSize + len(data['hits']['hits'])

        reports['Tested'] = totalSize
        print(f"Number of datasets tested: {reports['Tested']}")
        reports['Failed'] = len(reports['FailedIds'])
        print(f"Number of dataset with erros: {reports['Failed']}")

        if len(reports['FailedIds']) > 0:
            print(json.dumps(reports, indent=4))
            
        with open('error_reports.json', 'w') as outfile:
            json.dump(reports, outfile, indent=4)
    
        self.assertEqual(0, len(reports['FailedIds']))

if __name__ == '__main__':
    unittest.main()
