import unittest
import requests
import botocore
import boto3
import json
import urllib.parse
import os

from urllib.parse import urljoin

from tests.config import Config

error_report = {}
doc_link = 'https://github.com/ABI-Software/scicrunch-knowledge-testing/tree/doc_v1'
#the following should either be a falsy value or a string containg dataset number
checkDatasetOnly = False

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

MIMETYPE_WITH_THUMBNAILS = [ PLOT_FILE, SCAFFOLD_FILE, SCAFFOLD_VIEW_FILE]

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
        #For checking specific dataset

        "_source": [
            "item.curie",
            "item.name",
            "item.types",
            "objects.datacite",
            "objects.additional_mimetype",
            "objects.dataset",
            "pennsieve.version",
            "pennsieve.identifier",
            "pennsieve.uri"
        ]
    }

    if checkDatasetOnly:
        query = {
            "match": {
                "pennsieve.identifier.aggregate": {
                    "query": checkDatasetOnly
                }
           }
        }
        scicrunch_request["query"] = query

    return requests.post(urljoin(scicrunch_host, '_search?preference=abiknowledgetesting'), json=scicrunch_request, params=params, headers=headers)

def extract_bucket_name(original_name):
    return original_name.split('/')[2]

def map_mime_type(mime_type):
    if mime_type == '':
        return NOT_SPECIFIED

    if mime_type == NOT_SPECIFIED:
        return NOT_SPECIFIED

    lower_mime_type = mime_type.lower()

    if lower_mime_type in TEST_MIME_TYPES:
        return TEST_MIME_TYPES[lower_mime_type]

    return NOT_SPECIFIED

#Get file header response from s3 bucket
def getFileResponse(localPath, path, mime_type, bucket):
    try:
        head_response = s3.head_object(
            Bucket=bucket,
            Key=path,
            RequestPayer="requester"
        )

        if head_response and 'ResponseMetadata' in head_response \
            and 200 == head_response['ResponseMetadata']['HTTPStatusCode']:
            pass
        else:
            return {
                'Mimetype': mime_type,
                'Path': localPath,
                'Reason': 'Invalid response',
                'ReasonDetails': doc_link + '#reason-invalid-response'
            }
    except botocore.exceptions.ClientError as error:
        return {
            'Mimetype': mime_type,
            'Path': localPath,
            'Reason': f"{error}",
            'ReasonDetails': doc_link + '#reason-an-error-occurred-404-when-calling-the-headobject-operation-not-found'
        }
    return None

#Get the mimetype
def getObjectMimeType(obj):
    mime_type = obj.get('additional_mimetype', NOT_SPECIFIED)
    if mime_type != NOT_SPECIFIED:
        mime_type = mime_type.get('name')
    return  mime_type

#Check if any of the item in isSourceOf is a thumbnail for the object
def checkForThumbnail(obj, obj_list):
    local_mapped_type = map_mime_type(getObjectMimeType(obj))
    if local_mapped_type == THUMBNAIL_IMAGE:
        #Thumbnail found
        return True
    elif local_mapped_type == SCAFFOLD_VIEW_FILE:
        if 'dataset' in obj and 'path' in obj['dataset']:
            localPath = obj['dataset']['path']
            #Found view file, check for thumbnail
            if 'datacite' in obj and 'isSourceOf' in obj['datacite']:
                isSourceOf = obj['datacite']['isSourceOf']
                if 'relative' in isSourceOf and 'path' in isSourceOf['relative']:
                    for path in isSourceOf['relative']['path']:
                        actualPath = urllib.parse.urljoin(localPath, path)
                        found = next((i for i, item in enumerate(obj_list) if item['dataset']['path'] == actualPath), None)
                        if found and map_mime_type(getObjectMimeType(obj_list[found])):
                            return True
    
    return False

#Generate report for datacite in the object
def getDataciteReport(obj_list, obj, mapped_mimetype, filePath):
    keysToCheck = { 'isDerivedFrom': 0, 'isSourceOf': 0}
    reports = {'TotalErrors':0, 'ThumbnailError': 'None', 'ItemTested':0, 'isDerivedFrom': [], 'isSourceOf': [] }
    thumbnailFound = False

    if 'datacite' in obj:
        for key in keysToCheck:
            if key in obj['datacite']:
                keyObject = obj['datacite'][key]
                if 'relative' in keyObject and 'path' in keyObject['relative']:
                    for path in keyObject['relative']['path']:
                        keysToCheck[key] = keysToCheck[key] + 1
                        reports['ItemTested'] += 1
                        try:
                            actualPath = urllib.parse.urljoin(filePath, path)
                            found = next((i for i, item in enumerate(obj_list) if item['dataset']['path'] == actualPath), None)
                            if found == None:
                                reports[key].append(
                                    {
                                        'RelativePath': path,
                                        'Reason': 'Cannot find the path',
                                        'ReasonDetails': doc_link + '#reason-cannot-find-the-path'
                                    }
                                )
                                reports['TotalErrors'] +=1
                            elif key == 'isSourceOf':
                                #Check for thumbnail
                                thumbnailFound = checkForThumbnail(obj_list[found], obj_list)
                        except:
                            reports[key].append(
                                {
                                    'RelativePath': path,
                                    'Reason': 'Encounter a problem while looking for path',
                                    'ReasonDetails': doc_link + '#reason-encounter-a-problem-while-looking-for-path'
                                }
                            )
                            reports['TotalErrors'] +=1

        if mapped_mimetype in MIMETYPE_WITH_THUMBNAILS:
            if keysToCheck['isSourceOf'] == 0:
                reports['ThumbnailError'] = 'Missing isSourceOf entry'
                reports['ThumbnailErrorDetails'] = doc_link + '#thumbnailerror-missing-issourceof-entry'
                reports['TotalErrors'] +=1
            if thumbnailFound == False:
                reports['ThumbnailError'] = 'Thumbnail not found in isSourceOf'
                reports['ThumbnailErrorDetails'] = doc_link + '#thumbnailerror-thumbnail-not-found-in-issourceof'
                reports['TotalErrors'] +=1

    return reports

#Test object to check for any possible error
def testObj(obj_list, obj, mime_type, mapped_mime_type, prefix, bucket):
    dataciteReport = None
    fileResponse = None

    if 'dataset' in obj and 'path' in obj['dataset']:
        localPath = obj['dataset']['path']
        path = f"{prefix}/{localPath}"
        fileResponse = getFileResponse(localPath, path, mime_type, bucket)
        dataciteReport = getDataciteReport(obj_list, obj, mapped_mime_type, localPath)
        if dataciteReport['TotalErrors'] > 0:
            if fileResponse == None:
                fileResponse = {
                    'Mimetype': mime_type,
                    'Path': localPath,
                }
            fileResponse['DataciteReport'] = dataciteReport
    else:
        fileResponse = {
            'Mimetype': mime_type,
            'Path': 'Not found',
            'Reason': 'Cannot find path',
            'Reason': doc_link + '#reason-cannot-find-the-path'
        }
        
    return fileResponse

def test_obj_list(id, version, obj_list, scaffoldTag, bucket):
    objectErrors = []
    prefix = f"{id}/files"
    foundScaffold = False
    foundContextInfo = False
    datasetErrors = []

    for obj in obj_list:
        mime_type = getObjectMimeType(obj)
        mapped_mime_type =  map_mime_type(mime_type)
        if mapped_mime_type == NOT_SPECIFIED:
            pass
        else:
            if mapped_mime_type == SCAFFOLD_FILE:
                foundScaffold = True
            if mapped_mime_type == CONTEXT_FILE:
                foundContextInfo = True
            error = testObj(obj_list, obj, mime_type, mapped_mime_type, prefix, bucket)
            if error:
                objectErrors.append(error)
    
    if foundScaffold == True:
        if foundContextInfo == False:
            datasetErrors.append({
                'Reason': 'Contextual Information cannot be found while scaffold is present',
                'Details': doc_link + '#contextual-information-cannot-be-found-while-scaffold-is-present'
            })
        if scaffoldTag == False:
            datasetErrors.append({
                'Reason': 'Scaffold found in objects list but the dataset is not tagged with scaffold (types.item.name)',
                'Details': doc_link + '#scaffold-found-in-objects-list-but-the-dataset-is-not-tagged-with-scaffold-typesitemname'
            })
    elif scaffoldTag == True:
        datasetErrors.append({
            'Reason': 'Dataset is tagged with scaffold (types.item.name) but no scaffold can be found in the list of objects.',
            'Details': doc_link + '#dataset-is-tagged-with-scaffold-typesitemname-but-no-scaffold-can-be-found-in-the-list-of-objects'
        })


    numberOfErrors = len(objectErrors)
    fileReports = {
        'Total': numberOfErrors,
        'Objects': objectErrors
    }
    return {"FileReports": fileReports, "DatasetErrors": datasetErrors}
                
#Test the dataset 
def test_datasets_information(dataset):
    scaffoldTag = False
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
            if 'types' in source['item']:
                for type in source['item']['types']:
                    if 'name' in type and type['name'] == 'scaffold':
                        scaffoldTag = True

        if 'pennsieve' in source and 'version' in source['pennsieve'] and 'identifier' in source['pennsieve']:
            id = source['pennsieve']['identifier']
            version = source['pennsieve']['version']['identifier']
            report['Id'] = id
            report['Version'] = version
            bucket = S3_BUCKET_NAME
            if 'uri' in source['pennsieve']:
                bucket = extract_bucket_name(source['pennsieve']['uri'])
            if version:
                if 'objects' in source:
                    obj_list = source['objects']
                    obj_reports = test_obj_list(id, version, obj_list, scaffoldTag, bucket)
                    report['ObjectErrors'] = obj_reports['FileReports']
                    report['Errors'].extend(obj_reports["DatasetErrors"])
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
        reportOutput = 'reports/error_reports.json'
        reports = {'Tested': 0, 'Failed': 0, 'FailedIds':[], 'Datasets':[]}


        while keepGoing:
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
                print(f"Reports generated for {report['Id']}")
                if len(report['Errors']) > 0 or report['ObjectErrors']['Total'] > 0:
                    reports['FailedIds'].append(report['Id'])
                    reports['Datasets'].append(report)


        # Generate the report
        reports['Tested'] = totalSize
        print(f"Number of datasets tested: {reports['Tested']}")
        reports['Failed'] = len(reports['FailedIds'])
        print(f"Number of dataset with erros: {reports['Failed']}")
        if reports['Failed'] > 0:
            print(f"Failed Datasets: {reports['FailedIds']}")
            
        os.makedirs(os.path.dirname(reportOutput), exist_ok=True)
        with open(reportOutput, 'w') as outfile:
            json.dump(reports, outfile, indent=4)
    
        print(f"Full report has been generated at {reportOutput}")

        self.assertEqual(0, len(reports['FailedIds']))

if __name__ == '__main__':
    unittest.main()
