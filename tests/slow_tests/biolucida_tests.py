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
nameMapping = {}
doc_link = 'https://github.com/ABI-Software/scicrunch-knowledge-testing/tree/doc_v1'

S3_BUCKET_NAME = "pennsieve-prod-discover-publish-use1"

NOT_SPECIFIED = 'not-specified'

def get_dataset_info_pennsieve_identifier(identifier):

    headers = {'accept': 'application/json'}
    params = {'api_key': Config.SCICRUNCH_API_KEY}

    scicrunch_host = Config.SCICRUNCH_API_HOST + '/'

    scicrunch_request = {
        "query": {
            "term": {
                "pennsieve.identifier.aggregate": identifier
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
            "objects.dataset",
            "pennsieve.version",
            "pennsieve.identifier",
            "pennsieve.uri"
        ]
    }

    return requests.post(urljoin(scicrunch_host, '_search?preference=abiknowledgetesting'), json=scicrunch_request, params=params, headers=headers)

def extract_bucket_name(original_name):
    return original_name.split('/')[2]


#Test object to check for any possible error
def testBiolucida(id, version, obj, biolucida_id, bucket):
    fileResponse = None
    global pennsieveCache
    localPath = None
    imageName = None
    pageType = 'Redirect biolucidaviewer page'
    pennsievePath = None


    if not isinstance(obj, list):
        pageType = 'Directly file page'
        localPath = obj['dataset']['path']
        if f'files/{localPath}' in name_map:
            localPath = name_map[f'files/{localPath}']

    try:

        biolucida_response = requests.get(f'{Config.BIOLUCIDA_ENDPOINT}/image/{biolucida_id}')
        if not biolucida_response.status_code == 200:
            return {
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': 'Cannot get a valid request from Biolucida',
            }
            
        image_info = biolucida_response.json()

        if image_info['status'] == "permission denied":
            return {
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': 'Biolucida permission denied',
            }
        
        if 'name' in image_info:
            imageName = image_info['name']
            if imageName in biolucida_name_map:
                imageName = biolucida_name_map[imageName]
        else:
            return {
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': '{page_type}: Filename cannot be found on Biolucida'.format(page_type=pageType),
            }

        if isinstance(obj, list):
            for dataset_obj in obj:
                path = dataset_obj['dataset']['path']
                if f'files/{path}' in name_map:
                    path = name_map[f'files/{path}']
                if path.rfind('/') != -1:
                    # Path and name may be different
                    pathname_modified = ' '.join(re.findall('[.a-zA-Z0-9]+', path[path.rfind('/')+1:]))
                    imagename_modified = ' '.join(re.findall('[.a-zA-Z0-9]+', imageName))
                    # Either exact match or contains part of others
                    if pathname_modified == imagename_modified or imagename_modified in pathname_modified or pathname_modified in imagename_modified:
                        localPath = path
            if localPath is None:
                return {
                    'scicrunch_path': localPath,
                    'biolucida_id': biolucida_id,
                    'Reason': '{page_type}: Filename cannot be found on Scicrunch'.format(page_type=pageType),
                } 
                    
        scicrunch_filename = localPath[localPath.rfind('/')+1:]

        #Check if file path is consistent between scicrunch and biolucida
        if imageName != scicrunch_filename:
            fileResponse = {
                'scicrunch_path': localPath,
                'biolucida_id': biolucida_id,
                'Reason': 'Conflict between scicrunch and biolucida response',
                'Detail': '{page_type}: Biolucida filename ***{biolucida_filename}*** does not match the filename in scicrunch_path'.format(
                    page_type=pageType, biolucida_filename=imageName),
            }
            if "files/" not in localPath:
                localPath = "files/" + localPath
            if id not in nameMapping:
                nameMapping[id] = {}
            nameMapping[id][localPath] = localPath.rsplit("/", 1)[0] + "/" + imageName
        else:
            #now check if the file path is consistent between Pennsieve and
            #the other two
            filePath = localPath
            if "files/" not in localPath:
                filePath = "files/" + localPath
            folderPath = filePath.rsplit("/", 1)[0]
            files = []
            if folderPath in pennsieveCache:
                files = pennsieveCache[folderPath]
            else:
                fileUrl = '{api}/datasets/{id}/versions/{version}/files/browse?path={folderPath}'.format( 
                    api=Config.PENNSIEVE_API_HOST, id=id, version=version, folderPath=folderPath)
                file_response = requests.get(fileUrl)
                files_info = file_response.json()
                    #print(files_info)
                if 'files' in files_info:
                    files = files_info['files']

            if len(files) > 0:
                pennsieveCache[folderPath] = files
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
                    # When incomplete folderPath is used to request files
                    elif localFile['path'].lower() in lPath:
                        pennsievePath = localFile['path'].lower()
                if not foundFile:
                    fileResponse = {
                        'scicrunch_path': localPath,
                        'biolucida_id': biolucida_id,
                        'Reason': 'File path cannot be found on Pennsieve',
                    }
                    if pennsievePath is not None:
                        fileResponse['Detail'] = 'Possible path ***{pennsieve_path}*** is found on Pennsieve'.format(
                            pennsieve_path=pennsievePath)
            else:
                fileResponse = {
                    'scicrunch_path': localPath,
                    'biolucida_id': biolucida_id,
                    'Reason': 'Folder path cannot be found on Pennsieve',
                }
    except Exception as e:    
        fileResponse = {
            'scicrunch_path': localPath,
            'biolucida_id': biolucida_id,
            'Reason': str(e)
        }

    return fileResponse

def test_biolucida_list(id, version, obj_list, bucket):
    objectErrors = []
    foundBiolucida = False
    global pennsieveCache
    pennsieveCache = {}
    datasetErrors = []
    biolucidaIDFound = False
    biolucidaInfoFound = False
    biolucidaFound = False
    biolucida_ids = []
    dataset_images = []
    dataset_images_duplicate = []
    duplicateFound = False
    biolucidaViewerRedirect = False
    redirect_source = {}
    BIOLUCIDA_2D = [
        'image/jp2',
        'image/vnd.ome.xml+jp2'
    ]

    biolucida_response = requests.get(f'{Config.BIOLUCIDA_ENDPOINT}/imagemap/search_dataset/discover/{id}')
    if biolucida_response.status_code == 200:
        dataset_info = biolucida_response.json()
        if 'status' in dataset_info and dataset_info['status'] == "success":
            biolucidaInfoFound = True

    for obj in obj_list:
        biolucida = obj.get('biolucida', NOT_SPECIFIED)
        if biolucida != NOT_SPECIFIED:
            biolucida_id = biolucida.get('identifier')
            if biolucida_id:
                mimetype = obj.get('additional_mimetype')
                if mimetype:
                    if mimetype['name'] in BIOLUCIDA_2D:
                        mimetype_name = mimetype.get('name')
                        biolucida_ids.append(biolucida_id)
                        biolucidaIDFound = True
                        error = testBiolucida(id, version, obj, biolucida_id, bucket)
                        if error:
                            objectErrors.append(error)

    if biolucidaIDFound or biolucidaInfoFound:
        biolucidaFound = True

    if biolucidaIDFound and not biolucidaInfoFound:
        datasetErrors.append({
            'Reason': 'One or more Biolucida ID found in SciCrunch but no image information is found on biolucida server.'
        })
    if not biolucidaIDFound and biolucidaInfoFound:
        datasetErrors.append({
            'Reason': 'Image information found on Biolucida server but no image id is found on SciCrunch.',
            'Detail': 'Please see the list below for more information.'
        })
        biolucidaViewerRedirect = True
        scicrunch_response = get_dataset_info_pennsieve_identifier(id)
        scicrunch_dataset = scicrunch_response.json()
        redirect_source = scicrunch_dataset['hits']['hits'][0]['_source']

    if biolucidaViewerRedirect and 'objects' not in redirect_source:
        datasetErrors.append({
            'Reason': 'No objects are found on Scicrunch pennsieve identifier query response.'
        })

    if biolucidaInfoFound and 'dataset_images' in dataset_info:
        for image in dataset_info['dataset_images']:
            image_id = image['image_id']
            if image_id not in dataset_images:
                dataset_images.append(image_id)
                # Biolucida viewer redirect to find if the image name can be matched
                if biolucidaViewerRedirect and image_id not in biolucida_ids and 'objects' in redirect_source:
                    error = testBiolucida(id, version, redirect_source['objects'], image_id, bucket)
                    if error:
                        objectErrors.append(error)
            else:
                dataset_images_duplicate.append(image_id)
                duplicateFound = True

        if duplicateFound:
            datasetErrors.append({
                'Reason': 'Duplicate image ids are found on biolucida server',
                'Detail': 'Redundant image ids ***{ids}***'.format(ids=', '.join(set(dataset_images_duplicate)))
            })

    numberOfErrors = len(objectErrors)
    fileReports = {
        'Total': numberOfErrors,
        'Objects': objectErrors
    }
    return {"FileReports": fileReports, "DatasetErrors": datasetErrors, "BiolucidaFound": biolucidaFound}
                
#Test the dataset 
def test_datasets_information(dataset):
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
            report['Version'] = version
            bucket = S3_BUCKET_NAME
            if 'uri' in source['pennsieve']:
                bucket = extract_bucket_name(source['pennsieve']['uri'])
            if version:
                obj_list = source['objects'] if 'objects' in source else []
                obj_reports = test_biolucida_list(id, version, obj_list, bucket)
                report['ObjectErrors'] = obj_reports['FileReports']
                report['Errors'].extend(obj_reports["DatasetErrors"])
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
        nameMappingOutput = 'reports/biolucida_name_mapping.json'
        reports = {'Tested': 0, 'Failed': 0, 'FailedIds':[], 'Datasets':[]}
        testSize = 2000
        totalBiolucida = 0

        # '''
        # Test selected datasets
        # '''
        # scicrunch_datasets = open('reports/scicrunch_datasets.json')
        # datasets = json.load(scicrunch_datasets)
        # scicrunch_datasets.close()
        # dataset_list = [
        #     "22",
        #     # "296",
        #     # "64",
        #     # "109",
        #     # "90",
        #     # "304",
        #     # "137",
        #     # "175",
        #     # "125",
        #     "345",
        #     # "43",
        #     "82",
        #     # "107",
        #     # "77",
        #     "158",
        #     "321",
        #     # "37",
        #     "265",
        #     # "61",
        #     # "16",
        #     # "348",
        #     # "389",
        #     # "383",
        #     # "230",
        #     # "221",
        #     # "75",
        #     # "73",
        #     # "36",
        #     # "54",
        #     # "60",
        #     "234",
        #     # "240",
        #     # "56",
        #     # "205",
        #     # "21",
        #     # "97",
        #     # "32",
        #     # "85",
        #     # "162",
        #     # "89",
        #     # "369",
        #     # "29",
        #     # "367",
        #     "373",
        #     # "65",
        #     # "161",
        #     # "204",
        #     # "108",
        #     # "293",
        #     # "178",
        #     # "88",
        #     # "287",
        #     # "388"
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
        #         reports['Datasets'].append(report)

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
                    reports['Datasets'].append(report)

            totalSize = totalSize + len(data['hits']['hits'])

            if totalSize >= testSize:
                keepGoing = False

        # Generate the report
        reports['Tested'] = totalSize
        reports['Tested Datasets with Biolucida'] = totalBiolucida
        print(f"Number of datasets tested: {reports['Tested']}")
        reports['Failed'] = len(reports['FailedIds'])
        print(f"Number of dataset with erros: {reports['Failed']}")
        if reports['Failed'] > 0:
            print(f"Failed Datasets: {reports['FailedIds']}")
            
        os.makedirs(os.path.dirname(reportOutput), exist_ok=True)
        with open(reportOutput, 'w') as outfile:
            json.dump(reports, outfile, indent=4)

        if len(nameMapping) > 0:
            os.makedirs(os.path.dirname(nameMappingOutput), exist_ok=True)
            with open(nameMappingOutput, 'w') as outfile:
                json.dump(nameMapping, outfile, indent=4)
    
        print(f"Full report has been generated at {reportOutput}")

        self.assertEqual(0, len(reports['FailedIds']))

if __name__ == '__main__':
    unittest.main()
