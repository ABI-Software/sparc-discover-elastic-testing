import unittest
import requests
import botocore
import boto3
import json
import urllib.parse
import os
import re

from urllib.parse import urljoin

from tests.config import Config

doc_link = 'https://github.com/ABI-Software/scicrunch-knowledge-testing/tree/doc_v1'

s3 = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_KEY,
    aws_secret_access_key=Config.AWS_SECRET,
    region_name="us-east-1",
)

S3_BUCKET_NAME = "prd-sparc-discover50-use1"

NOT_SPECIFIED = 'not-specified'

PLOT_FILE = [
    'text/vnd.abi.plot+tab-separated-values', 
    'text/vnd.abi.plot+csv'
]
# mimetype: additional_mimetype
COMMON_TO_THUMBNAIL = {
    'image/jpeg': 'image/x.vnd.abi.thumbnail+jpeg', 
    'image/png': 'image/x.vnd.abi.thumbnail+png'
}

def get_datasets(start, size):

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
            "objects.name",
            "objects.datacite",
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

def test_plot_thumbnail_s3file(dataset_id, thumbnail_object, s3_bucket):
    scicrunch_path = thumbnail_object['dataset']['path']
    if "files/" not in scicrunch_path:
        scicrunch_path = "files/" + scicrunch_path
    scicrunch_path = f'{dataset_id}/' + scicrunch_path

    try:
        head_response = s3.head_object(
            Bucket=s3_bucket,
            Key=scicrunch_path,
            RequestPayer="requester"
        )
        if head_response and 'ResponseMetadata' in head_response and 200 == head_response['ResponseMetadata']['HTTPStatusCode']:
            pass
        else:
            return {
                'S3Path': scicrunch_path,
                'Reason': 'Invalid response',
            }
    except botocore.exceptions.ClientError as error:
        return {
            'S3Path': scicrunch_path,
            'Reason': f"{error}",
        }

    return None

def test_plot_thumbnail(dataset_id, plot_object, object_list, s3_bucket):
    responses = []

    thumbnail_name = None
    thumbnail_scicrunch_path = None

    plot_scicrunch_path = plot_object['dataset']['path']
    is_source_of = plot_object['datacite']['isSourceOf'].get('path', NOT_SPECIFIED)

    if "files/" not in plot_scicrunch_path:
        plot_scicrunch_path = "files/" + plot_scicrunch_path
    if is_source_of != NOT_SPECIFIED:
        thumbnail_name = is_source_of[0].split('/')[-1]

    for thumbnail_object in object_list:
        # Plot file should be the source of the thumbnail
        if thumbnail_name and thumbnail_name == thumbnail_object.get('name'):
            thumbnail_scicrunch_path = thumbnail_object['dataset']['path']
            if "files/" not in thumbnail_scicrunch_path:
                thumbnail_scicrunch_path = "files/" + thumbnail_scicrunch_path

            # Plot thumbnail should be derived from the plot file
            plot_path = thumbnail_object['datacite']['isDerivedFrom'].get('path', NOT_SPECIFIED)
            if plot_path == NOT_SPECIFIED or plot_object['name'] not in plot_path[0]:
                return [{
                    'PlotPath': plot_scicrunch_path,
                    'ThumbnailPath': thumbnail_scicrunch_path,
                    'Reason': 'Thumbnail isDerivedFrom does not contain correct plot name.',
                }]

            # Check if additional mimetype is valid in sparc api
            mime_type = thumbnail_object.get('additional_mimetype', NOT_SPECIFIED)
            if mime_type != NOT_SPECIFIED:
                mime_type = mime_type.get('name')
            if not mime_type or mime_type not in COMMON_TO_THUMBNAIL.values():
                error_response = {
                    'PlotPath': plot_scicrunch_path,
                    'ThumbnailPath': thumbnail_scicrunch_path,
                    'Reason': f'Thumbnail additional mimetype *** {mime_type} *** is no longer processed in sparc api.',
                    'UpdateRequired': 'Check following detail for more information.'
                }
                # Figure out the correct additional mimetype by using mimetype
                mime_type = thumbnail_object['mimetype'].get('name', NOT_SPECIFIED)
                if mime_type in COMMON_TO_THUMBNAIL.keys():
                    error_response['UpdateDetail'] = f'Correct additional mimetype should be *** {COMMON_TO_THUMBNAIL[mime_type]} ***.'
                responses.append(error_response)

                # Check if the file exists in s3
                error = test_plot_thumbnail_s3file(dataset_id, thumbnail_object, s3_bucket)
                if error:
                    responses.append(error)

                return responses

def test_plot_list(dataset_id, object_list, s3_bucket):
    objectErrors = []
    datasetErrors = []

    PlotFound = False

    for plot_object in object_list:
        # Check if the object is a segmentation file
        mime_type = plot_object.get('additional_mimetype', NOT_SPECIFIED)
        if mime_type != NOT_SPECIFIED:
            mime_type = mime_type.get('name')
        if not mime_type:
            mime_type = plot_object['mimetype'].get('name', NOT_SPECIFIED)

        if mime_type in PLOT_FILE:
            PlotFound = True
            error = test_plot_thumbnail(dataset_id, plot_object, object_list, s3_bucket)
            if error:
                objectErrors.extend(error)

    numberOfErrors = len(objectErrors)
    fileReports = {
        'Total': numberOfErrors,
        'Objects': objectErrors,
    }

    return {"FileReports": fileReports, "DatasetErrors": datasetErrors, "PlotFound": PlotFound}
                
#Test the dataset 
def test_datasets_information(dataset):
    report = {
        'Id': 'none',
        'DOI': 'none',
        '_id': dataset['_id'],
        'Errors': [],
        'ObjectErrors': {'Total': 0, 'Objects':[]}
    }
    if '_source' in dataset:
        source = dataset['_source']
        if 'item' in source:
            report['Name'] = source['item'].get('name', 'none')
            report['DOI'] = source['item'].get('curie', 'none')

        if 'pennsieve' in source and 'version' in source['pennsieve'] and 'identifier' in source['pennsieve']:
            dataset_id = source['pennsieve']['identifier']
            version = source['pennsieve']['version']['identifier']
            report['Id'] = dataset_id
            report['Version'] = version
            s3_bucket = S3_BUCKET_NAME
            if 'uri' in source['pennsieve']:
                s3_bucket = extract_bucket_name(source['pennsieve']['uri'])
            if version:
                object_list = source['objects'] if 'objects' in source else []
                object_reports = test_plot_list(dataset_id, object_list, s3_bucket)
                report['ObjectErrors'] = object_reports['FileReports']
                report['Errors'].extend(object_reports["DatasetErrors"])
                report['Plot'] = object_reports['PlotFound']
            else:
                report['Errors'].append('Missing version')
    return report


class PlotDatasetFilesTest(unittest.TestCase):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def test_files_information(self):
        global path_mapping
        start = 0
        size = 20
        keepGoing = True
        totalSize = 0
        reportOutput = 'reports/plot_reports.json'
        pathMappingOutput = 'reports/plot_path_mapping.json'
        reports = {'Tested': 0, 'Failed': 0, 'FailedIds':[], 'Datasets':[]}
        testSize = 2000
        totalPlot = 0

        # '''
        # Test selected datasets
        # '''
        # scicrunch_datasets = open('reports/scicrunch_datasets.json')
        # datasets = json.load(scicrunch_datasets)
        # scicrunch_datasets.close()
        # # dataset_list = list(datasets.keys())
        # dataset_list = [
        #     '212', 
        #     '26', 
        #     '148', 
        #     '114', 
        #     '126', 
        #     '139', 
        #     '142', 
        #     '46', 
        #     '117', 
        #     '29', 
        #     '132', 
        #     '118', 
        #     '119'
        # ]

        # '''
        # Add datasets to the queue
        # '''
        # data = {'hits': {'hits': []}}
        # for dataset_id in dataset_list:
        #     data['hits']['hits'].append(datasets[dataset_id])

        # for dataset in data['hits']['hits']:
        #     report = test_datasets_information(dataset)
        #     if 'Plot' in report and report['Plot']:
        #         totalPlot = totalPlot + 1
        #     print(f"Reports generated for {report['Id']}")
        #     if len(report['Errors']) > 0 or report['ObjectErrors']['Total'] > 0:
        #         reports['FailedIds'].append(report['Id'])
        #         reports['Datasets'].append(report)

        # totalSize = totalSize + len(data['hits']['hits'])

        '''
        Test all the datasets
        '''
        while keepGoing :
            scicrunch_response = get_datasets(start, size)
            self.assertEqual(200, scicrunch_response.status_code)

            data = scicrunch_response.json()

            #No more result, stop
            if size > len(data['hits']['hits']):
                keepGoing = False

            #keepGoing= False

            start = start + size

            for dataset in data['hits']['hits']:
                report = test_datasets_information(dataset)
                if 'Plot' in report and report['Plot']:
                    totalPlot = totalPlot + 1
                print(f"Reports generated for {report['Id']}")
                if len(report['Errors']) > 0 or report['ObjectErrors']['Total'] > 0:
                    reports['FailedIds'].append(report['Id'])
                    reports['Datasets'].append(report)

            totalSize = totalSize + len(data['hits']['hits'])

            if totalSize >= testSize:
                keepGoing = False

        # Generate the report
        reports['Tested'] = totalSize
        reports['Tested Datasets with Plot'] = totalPlot
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
