import unittest
import requests
import json
import urllib.parse
import os
import re

from urllib.parse import urljoin

from tests.config import Config
from tests.slow_tests.manifest_name_to_discover_name import name_map, biolucida_name_map

pennsieveCache = {}
pennsieveMetadataCache = {}
nameMapping = {
    'Note': {
        'Format': {
            "dataset_id": {
                "biolucida_id": {
                    "scicrunch_file_path" : {
                        "image_name_in_biolucida": "filename_in_scicrunch_file_path"
                    }
                }
            }
        },
        'Message': 'Not all listed name mappings are required. Better to go through the mapping file and check before using in the sparc api.'
    }
}
pathMapping = {}
doc_link = 'https://github.com/ABI-Software/scicrunch-knowledge-testing/tree/doc_v1'

S3_BUCKET_NAME = "pennsieve-prod-discover-publish-use1"

NOT_SPECIFIED = 'not-specified'

BIOLUCIDA_2D = [
    'image/jp2',
    'image/vnd.ome.xml+jp2'
]
BIOLUCIDA_3D = [
    'image/jpx',
    'image/vnd.ome.xml+jpx'
]

# Set to True if you want to use the mapping implementation
# This will requirer the mapping file to be present in the same directory
# And make sure the mapping file is up-to-date.
MAPPING_IMPLEMENTATION = False
IMAGE_MAPPING_IMPLEMENTATION = False

def get_dataset_info_pennsieve_identifier(dataset_id):

    headers = {'accept': 'application/json'}
    params = {'api_key': Config.SCICRUNCH_API_KEY}

    scicrunch_host = Config.SCICRUNCH_API_HOST + '/'

    scicrunch_request = {
        "query": {
            "term": {
                "pennsieve.identifier.aggregate": dataset_id
            }
        },
        "_source": [
            "objects.dataset"
        ]
    }

    return requests.post(urljoin(scicrunch_host, '_search?preference=abiknowledgetesting'), json=scicrunch_request, params=params, headers=headers)

def getDatasets(start, size):

    headers = {'accept': 'application/json'}
    params = {'api_key': Config.SCICRUNCH_API_KEY}

    scicrunch_host = Config.SCICRUNCH_API_HOST + '/'

    scicrunch_request = {
        "from": start,
        "size": size,
        "_source": [
            "item.curie",
            "item.name",
            "item.types",
            "objects.biolucida",
            "objects.additional_mimetype",
            "objects.mimetype",
            "objects.dataset",
            "pennsieve.version",
            "pennsieve.identifier",
            "pennsieve.uri"
        ]
    }

    return requests.post(urljoin(scicrunch_host, '_search?preference=abiknowledgetesting'), json=scicrunch_request, params=params, headers=headers)

def extract_bucket_name(original_name):
    return original_name.split('/')[2]

def compareWithMetadataFromPennsieve(dataset_id, version, fileName, filePath):
    global pennsieveMetadataCache
    global pathMapping
    error_response = {}
    files_metadata = []
    key = f'{dataset_id}_{version}'

    if key in pennsieveMetadataCache:
        files_metadata = pennsieveMetadataCache[key]
    else:
        metadata_response = requests.get(f'{Config.PENNSIEVE_API_HOST}/datasets/{dataset_id}/versions/{version}/metadata')
        metadata_info = metadata_response.json()
        #print(metadata_info)
        if 'files' in metadata_info:
            files_metadata = metadata_info['files']
            if len(files_metadata) > 0:
                pennsieveMetadataCache[key] = files_metadata

    # If the file path is exist in the metadata, add it to the mapping file
    if len(files_metadata) > 0:
        for file_metadata in files_metadata:
            modified_fileName = ' '.join(re.findall('[.a-zA-Z0-9]+', fileName))
            modified_metadata_path = ' '.join(re.findall('[.a-zA-Z0-9]+', file_metadata['path']))
            if fileName in file_metadata['path'] or modified_fileName in modified_metadata_path:
                if dataset_id not in pathMapping:
                    pathMapping[dataset_id] = {}
                pathMapping[dataset_id][filePath] = file_metadata['path']
                error_response['Detail'] = f'Correct file path is found through Pennsieve metadata.'
                error_response['PathMappingRequired'] = 'Please check the path mapping file output for more information.'
                if filePath in name_map:
                    error_response['PathMappingSolved'] = 'This is a known inconsistency issue which has been manually mapped in the sparc api.'
                return error_response

def fetchFilesFromPennsieve(dataset_id, version, folderPath):
    global pennsieveCache
    files = []

    if folderPath in pennsieveCache:
        files = pennsieveCache[folderPath]
    else:
        fileUrl = '{api}/datasets/{id}/versions/{version}/files/browse?path={folderPath}'.format( 
            api=Config.PENNSIEVE_API_HOST, id=dataset_id, version=version, folderPath=folderPath)
        file_response = requests.get(fileUrl)
        files_info = file_response.json()
        #print(files_info)
        if 'files' in files_info:
            files = files_info['files']
            if len(files) > 0:
                pennsieveCache[folderPath] = files

    return files
    
def testScicrunchAndPennsieve(localPath, dataset_id, version, biolucida_id):
    error_response = {
        'scicrunch_path': localPath,
        'biolucida_id': biolucida_id,
    }
    # Check if the file path is consistent between Scicrunch and Pennsieve
    filePath = localPath
    folderPath = filePath.rsplit("/", 1)[0]
    fileName = filePath.rsplit("/", 1)[1]

    files = fetchFilesFromPennsieve(dataset_id, version, folderPath)

    if len(files) > 0:
        lPath = filePath.lower()
        foundFile = False
        for localFile in files:
            if lPath == localFile['path'].lower():
                foundFile = True
                break
            elif 'uri' in localFile:
                uriFile = localFile['uri'].rsplit("/", 1)[0]
                if uriFile:
                    uriFile = uriFile.lower()
                    if uriFile in filePath:
                        foundFile = True
                        break
        if not foundFile:
            error_response['Reason'] = 'File path cannot be found on Pennsieve.'
            compare_response = compareWithMetadataFromPennsieve(dataset_id, version, fileName, filePath)
            if compare_response:
                error_response.update(compare_response)
            return error_response
    else:
        error_response['Reason'] = 'Folder path cannot be found on Pennsieve.'
        compare_response = compareWithMetadataFromPennsieve(dataset_id, version, fileName, filePath)
        if compare_response:
            error_response.update(compare_response)
        return error_response

def testBiolucidaAndScicrunch(imageName, localPath, dataset_id, biolucida_id, navigate_type):
    global nameMapping
    filePath = localPath

    # When mapping not implemented, use the pathMapping cache to get the Pennsieve file path to compare with Biolucida
    # This should figure out the correct image name mapping
    if not MAPPING_IMPLEMENTATION and dataset_id in pathMapping and filePath in pathMapping[dataset_id]:
        filePath = pathMapping[dataset_id][filePath]

    if imageName != filePath.split("/")[-1]:
        error_response = {
            'scicrunch_path': localPath,
            'biolucida_id': biolucida_id,
            'Reason': 'Conflict between scicrunch and biolucida response.',
            'Detail': f'{navigate_type}: Biolucida filename does not match with the filename in Pennsieve-mapped Scicrunch path.',
        }

        # Then generate the name mapping between Biolucida and Scicrunch
        if dataset_id not in nameMapping:
            nameMapping[dataset_id] = {}
        if biolucida_id not in nameMapping[dataset_id]:
            nameMapping[dataset_id][biolucida_id] = {}
        if filePath not in nameMapping[dataset_id][biolucida_id]:
            nameMapping[dataset_id][biolucida_id][filePath] = {}
        nameMapping[dataset_id][biolucida_id][filePath][imageName] = filePath.split("/")[-1]

        error_response['NameMappingRequired'] = 'Please check the name mapping file output for more information.'
        if imageName in biolucida_name_map:
            error_response['NameMappingSolved'] = 'This is a known inconsistency issue which has been manually mapped in the sparc api.'
        return error_response

#Test object to check for any possible error
def testBiolucida(dataset_id, version, obj, biolucida_id, bucket, mimetype):
    fileErrors = []
    fileResponse = None
    localPath = None
    imageName = None
    navigate_type = 'Direct to FILE VIEWER' if mimetype in BIOLUCIDA_2D else 'Redirect via BIOLUCIDA VIEWER'

    localPath = obj['dataset']['path']
    if "files/" not in localPath:
        localPath = "files/" + localPath
    # Use the mapping file to get the correct file path
    if MAPPING_IMPLEMENTATION and localPath in name_map:
        localPath = name_map[localPath]

    try:
        biolucida_response = requests.get(f'{Config.BIOLUCIDA_ENDPOINT}/image/{biolucida_id}')
        if not biolucida_response.status_code == 200:
            return [{
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': f'{navigate_type}: Cannot get a valid request from Biolucida.',
            }]
            
        image_info = biolucida_response.json()

        if image_info['status'] == "permission denied":
            return [{
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': f'{navigate_type}: Biolucida permission denied.',
            }]

        if 'name' in image_info:
            imageName = image_info['name']
            # Use the mapping file to get the correct image name
            if IMAGE_MAPPING_IMPLEMENTATION and imageName in biolucida_name_map:
                imageName = biolucida_name_map[imageName]

        else:
            return [{
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': f'{navigate_type}: Image name cannot be found on Biolucida.',
            }]

        spError = testScicrunchAndPennsieve(localPath, dataset_id, version, biolucida_id)
        if spError:
            fileErrors.append(spError)

        # If duplicate biolucida found in Scicrunch.
        # Following test will not be suitable for this case.
        # Need to think of a better way to handle this.
        bsError = testBiolucidaAndScicrunch(imageName, localPath, dataset_id, biolucida_id, navigate_type)
        if bsError:
            fileErrors.append(bsError)

    except Exception as e:    
        fileResponse = {
            'scicrunch_path': localPath,
            'biolucida_id': biolucida_id,
            'Reason': str(e)
        }
        fileErrors.append(fileResponse)
    return fileErrors

def test_biolucida_list(dataset_id, version, obj_list, bucket):
    DatasetWarnings = []
    datasetErrors = []
    objectErrors = []
    global pennsieveCache
    pennsieveCache = {}
    biolucidaObjectFound  = False # check if biolucida id is found in scicrunch
    biolucidaIDMatch   = True # check if biolucida id is match with scicrunch
    biolucidaImageFound  = False # check if biolucida information is found in biolucida server
    biolucidaFound = False
    duplicateFound = False
    biolucida_ids = [] # ids in Biolucida server only
    scicrunch_ids = [] # ids in both Scicrunch only
    bipresence_ids = [] # ids in both Scicrunch and Biolucida server
    duplicate_biolucida = [] # duplicate in Scicrunch

    biolucida_response = requests.get(f'{Config.BIOLUCIDA_ENDPOINT}/imagemap/search_dataset/discover/{dataset_id}')
    if biolucida_response.status_code == 200:
        dataset_info = biolucida_response.json()
        if 'status' in dataset_info and dataset_info['status'] == "success":
            biolucidaImageFound  = True
            # A list if ids of all images in the dataset
            biolucida_ids = [image.get('image_id', None) for image in dataset_info['dataset_images']]

    # This is object list from Scicrunch
    for obj in obj_list:
        biolucida = obj.get('biolucida', NOT_SPECIFIED)
        if biolucida != NOT_SPECIFIED:
            biolucida_id = biolucida.get('identifier')
            if biolucida_id:
                biolucidaObjectFound  = True
                if biolucida_id in biolucida_ids:
                    # Check if the object is a biolucida object
                    mime_type = obj.get('additional_mimetype', NOT_SPECIFIED)
                    if mime_type != NOT_SPECIFIED:
                        mime_type = mime_type.get('name')
                    if not mime_type:
                        mime_type = obj['mimetype'].get('name', NOT_SPECIFIED)

                    if (mime_type in BIOLUCIDA_2D or mime_type in BIOLUCIDA_3D):
                        # Check for duplicate biolucida
                        if biolucida_id in bipresence_ids:
                            duplicate_biolucida.append(biolucida_id)
                            duplicateFound = True
                        else:
                            bipresence_ids.append(biolucida_id)

                        # All the names/paths will based on Pennsieve
                        #   (3d)   name   (2d)  path
                        # biolucida -> scicrunch -> pennsieve
                        #     ^                        |
                        #     |                        |
                        #     +-----------<------------+
                        #                name

                        error = testBiolucida(dataset_id, version, obj, biolucida_id, bucket, mime_type)
                        if error:
                            objectErrors.extend(error)
                elif biolucida_id not in biolucida_ids:
                    biolucidaIDMatch = False
                    scicrunch_ids.append(biolucida_id)

    if biolucidaObjectFound  or biolucidaImageFound :
        biolucidaFound = True

    if biolucidaObjectFound  and not biolucidaImageFound :
        DatasetWarnings.append({
            'Reason': 'One or more Biolucida ID found on SciCrunch but no image information is found on Biolucida server.',
            'Detail': 'No Biolucida images will be displayed. Biolucida server data update may required.'
        })

    if biolucidaObjectFound and biolucidaImageFound and not biolucidaIDMatch :
        DatasetWarnings.append({
            'Reason': 'Specific Biolucida ID found on SciCrunch but no image information is found on Biolucida server.',
            'Detail': 'No Biolucida images will be displayed. Biolucida server data update may required.'
        })

    if not biolucidaObjectFound  and biolucidaImageFound :
        DatasetWarnings.append({
            'Reason': 'Image information is found on Biolucida server but no Biolucida ID is found on SciCrunch.',
            'Detail': 'No Biolucida images will be displayed. Scicrunch metadata update may required.'
        })

    if duplicateFound:
        # Duplicate objects have same biolucida id but name may be different
        # Remove the object errors for duplicate images
        # Remove the name mapping for duplicate images
        remain_errors = []
        for error in objectErrors:
            if error['biolucida_id'] in duplicate_biolucida and 'Conflict between' in error['Reason']:
                pass
            else:
                remain_errors.append(error)
        objectErrors = remain_errors
        
        if dataset_id in nameMapping:
            for biolucida_id in duplicate_biolucida:
                if biolucida_id in nameMapping[dataset_id]:
                    del nameMapping[dataset_id][biolucida_id]
            if len(nameMapping[dataset_id]) == 0:
                del nameMapping[dataset_id]

        datasetErrors.append({
            'Reason': 'Duplicate image ids are found on Scicrunch.',
            'Detail': 'Redundant images are found on {ids}.'.format(ids=', '.join(set(duplicate_biolucida))),
            'Total': len(duplicate_biolucida),
            'Further': 'Same biolucida id but different name may cause further issues in thumbnail or viewer.'
        })

    numberOfErrors = len(objectErrors)
    fileReports = {
        'Total': numberOfErrors,
        'Objects': objectErrors
    }
    numberOfInconsistency = 0
    numberOfNameInconsistency = 0
    numberOfPathInconsistency = 0
    numberOfNameMapped = 0
    numberOfPathMapped = 0
    for error in objectErrors:
        if 'NameMappingRequired' in error:
            numberOfNameInconsistency += 1
        if 'PathMappingRequired' in error:
            numberOfPathInconsistency += 1
        if 'NameMappingSolved' in error:
            numberOfNameMapped += 1
        if 'PathMappingSolved' in error:
            numberOfPathMapped += 1
    numberOfInconsistency = numberOfNameInconsistency + numberOfPathInconsistency
    if numberOfInconsistency > 0:
        fileReports['Inconsistency'] = {
            'Total': numberOfInconsistency,
        }
        if numberOfNameInconsistency > 0:
            fileReports['Inconsistency']['Name'] = {
                'Total': numberOfNameInconsistency,
                'NameMapped': numberOfNameMapped,
                'NameUnMapped': numberOfNameInconsistency - numberOfNameMapped,
            }
        if numberOfPathInconsistency > 0:
            fileReports['Inconsistency']['Path'] = {
                'Total': numberOfPathInconsistency,
                'NameMapped': numberOfPathMapped,
                'NameUnMapped': numberOfPathInconsistency - numberOfPathMapped,
            }
    return {"FileReports": fileReports, "DatasetWarnings": DatasetWarnings, "DatasetErrors": datasetErrors, "BiolucidaFound": biolucidaFound}
                
#Test the dataset 
def test_datasets_information(dataset):
    report = {
        'Id': 'none',
        'DOI': 'none',
        '_id': dataset['_id'],
        'Warnings': [],
        'Errors': [],
        'ObjectErrors': {'Total': 0, 'Objects':[]}
    }
    if '_source' in dataset :
        source = dataset['_source']
        if 'item' in source:
            report['Name'] = source['item'].get('name', 'none')
            report['DOI'] = source['item'].get('curie', 'none')

        if 'pennsieve' in source and 'version' in source['pennsieve'] and 'identifier' in source['pennsieve']:
            dataset_id = source['pennsieve']['identifier']
            version = source['pennsieve']['version']['identifier']
            report['Id'] = dataset_id
            report['Version'] = version
            bucket = S3_BUCKET_NAME
            if 'uri' in source['pennsieve']:
                bucket = extract_bucket_name(source['pennsieve']['uri'])
            if version:
                obj_list = source['objects'] if 'objects' in source else []
                obj_reports = test_biolucida_list(dataset_id, version, obj_list, bucket)
                report['Warnings'].extend(obj_reports["DatasetWarnings"])
                report['Errors'].extend(obj_reports["DatasetErrors"])
                report['ObjectErrors'] = obj_reports['FileReports']
                report['Biolucida'] = obj_reports['BiolucidaFound']
            else:
                report['Errors'].append('Missing version')
    return report


class BiolucidaDatasetFilesTest(unittest.TestCase):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def test_files_information(self):

        start = 0
        size = 20
        keepGoing = True
        totalSize = 0
        reportOutput = 'reports/biolucida_reports.json'
        nameMappingOutput = 'reports/biolucida_name_mapping.json' # replace Biolucida name with Scicrunch filename
        pathMappingOutput = 'reports/biolucida_path_mapping.json' # replace Scicrunch file path with Pennsieve file path
        reports = {'Tested': 0, 'Warned': 0, 'Failed': 0, 'WarnedIds':[], 'FailedIds':[], 'WarnedDatasets':[], 'FailedDatasets':[]}
        testSize = 2000
        totalBiolucida = 0

        # '''
        # Test selected datasets
        # '''
        # scicrunch_datasets = open('reports/scicrunch_datasets.json')
        # datasets = json.load(scicrunch_datasets)
        # scicrunch_datasets.close()
        # # dataset_list = list(datasets.keys())
        # dataset_list = [
        #     # warning
        #     "22",
        #     "296",
        #     "64",
        #     "109",
        #     "90",
        #     "304",
        #     "137",
        #     "175",
        #     "43",
        #     "82",
        #     "332",
        #     "77",
        #     "187",
        #     "37",
        #     "61",
        #     "290",
        #     "16",
        #     "348",
        #     "366",
        #     "383",
        #     "230",
        #     "125",
        #     "75",
        #     "73",
        #     "36",
        #     "54",
        #     "60",
        #     "234",
        #     "240",
        #     "56",
        #     "21",
        #     "97",
        #     "32",
        #     "85",
        #     "89",
        #     "369",
        #     "29",
        #     "367",
        #     "388",
        #     "386",
        #     "161",
        #     "293",
        #     "88",
        #     "382",
        #     "385",
        #     "287",
        #     # fail
        #     "345",
        #     "107",
        #     "158",
        #     "321",
        #     "265",
        #     "381",
        #     "389",
        #     "221",
        #     "205",
        #     "373",
        #     "65",
        #     "204",
        #     "108",
        #     "178"
        # ]

        # '''
        # Add datasets to the queue
        # '''
        # data = {'hits': {'hits': []}}
        # for dataset_id in dataset_list:
        #     data['hits']['hits'].append(datasets[dataset_id])

        # for dataset in data['hits']['hits']:
        #     report = test_datasets_information(dataset)
        #     if 'Biolucida' in report and report['Biolucida']:
        #         totalBiolucida = totalBiolucida + 1
        #     print(f"Reports generated for {report['Id']}")
        #     if len(report['Errors']) > 0 or report['ObjectErrors']['Total'] > 0:
        #         reports['FailedIds'].append(report['Id'])
        #         reports['FailedDatasets'].append(report)
        #     else:
        #         if len(report['Warnings']) > 0:
        #             reports['WarnedIds'].append(report['Id'])
        #             reports['WarnedDatasets'].append(report)

        # totalSize = totalSize + len(data['hits']['hits'])

        # if totalSize >= testSize:
        #     keepGoing = False

        '''
        Test all the datasets
        '''
        while keepGoing :
            scicrunch_response = getDatasets(start, size)
            self.assertEqual(200, scicrunch_response.status_code)

            data = scicrunch_response.json()

            #No more result, stop
            if size > len(data['hits']['hits']):
                keepGoing = False

            #keepGoing= False

            start = start + size

            for dataset in data['hits']['hits']:
                report = test_datasets_information(dataset)
                if 'Biolucida' in report and report['Biolucida']:
                    totalBiolucida = totalBiolucida + 1
                print(f"Reports generated for {report['Id']}")
                if len(report['Errors']) > 0 or report['ObjectErrors']['Total'] > 0:
                    reports['FailedIds'].append(report['Id'])
                    reports['FailedDatasets'].append(report)
                else:
                    if len(report['Warnings']) > 0:
                        reports['WarnedIds'].append(report['Id'])
                        reports['WarnedDatasets'].append(report)

            totalSize = totalSize + len(data['hits']['hits'])

            if totalSize >= testSize:
                keepGoing = False

        # Generate the report
        reports['Tested'] = totalSize
        reports['Tested Datasets with Biolucida'] = totalBiolucida
        print(f"Number of datasets tested: {reports['Tested']}")
        reports['Warned'] = len(reports['WarnedIds'])
        reports['Failed'] = len(reports['FailedIds'])
        print(f"Number of dataset with warning: {reports['Warned']}")
        print(f"Number of dataset with errors: {reports['Failed']}")
        if reports['Warned'] > 0:
            print(f"Warned Datasets: {reports['WarnedIds']}")
        if reports['Failed'] > 0:
            print(f"Failed Datasets: {reports['FailedIds']}")
            
        os.makedirs(os.path.dirname(reportOutput), exist_ok=True)
        with open(reportOutput, 'w') as outfile:
            json.dump(reports, outfile, indent=4)

        os.makedirs(os.path.dirname(nameMappingOutput), exist_ok=True)
        with open(nameMappingOutput, 'w') as outfile:
            json.dump(nameMapping, outfile, indent=4)

        os.makedirs(os.path.dirname(pathMappingOutput), exist_ok=True)
        with open(pathMappingOutput, 'w') as outfile:
            json.dump(pathMapping, outfile, indent=4)
    
        print(f"Full report has been generated at {reportOutput}")

        self.assertEqual(0, len(reports['FailedIds']))

if __name__ == '__main__':
    unittest.main()
