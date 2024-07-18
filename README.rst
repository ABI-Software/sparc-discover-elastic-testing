===========================
SciCrunch Knowledge Testing
===========================

This repository holds tests for the knowledge provided from SciCrunch endpoints.

.. contents:: Table of Contents
------------------------------------
SPARC Discover and SciCrunch Testing
------------------------------------
Datasets on Discover compared to the knowledge on SciCrunch.

Required Environment variables
==============================
The following environment variables need to be set to the appropriate values for the tests to run::

 PENNSIEVE_API_HOST
 PENNSIEVE_API_SECRET
 PENNSIEVE_API_TOKEN
 SCICRUNCH_API_HOST
 SCICRUNCH_API_KEY
 ALGOLIA_KEY
 ALGOLIA_ID
 ALGOLIA_INDEX
 AWS_SECRET
 AWS_KEY

Where *PENNSIEVE_API_HOST* could be set to *https://api.pennsieve.io/discover*, and *SCICRUNCH_API_HOST* could be set to *https://scicrunch.org/api/1/elastic/SPARC_PortalDatasets_dev*.
The other environment variables *PENNSIEVE_API_SECRET*, *PENNSIEVE_API_TOKEN*, and *SCICRUNCH_API_KEY* you will need to figure out for yourself.

Running the fast/nightly tests
==============================
 python -m unittest discover -s tests/nightly_tests

Running the slow tests
======================

Datasets object tests Information
---------------------------------
 python -m unittest tests/slow_tests/test_datasets_tests.py

Biolucida tests Information
---------------------------------
 python -m unittest tests/slow_tests/biolucida_tests.py

Segmentation tests Information
---------------------------------
 python -m unittest tests/slow_tests/segmentation_tests.py

Plot tests Information
---------------------------------
 python -m unittest tests/slow_tests/plot_tests.py

Details on slow tests reports
=============================
There are number of different errors in the `slow tests reports <https://autotest.bioeng.auckland.ac.nz/jenkins/view/Web%20Portal/job/Weekly%20SciCrunch%20Knowledge%20Test/21/artifact/reports/error_reports.json>`_,
this section provides an overview of the reports structures and details for the errors..

Top Level Information
---------------------
Four fields at the top level of the reports:

  - Tested: Number of datasets Tested
  - Failed: Number of failed datasets
  - FailedIds: List of id for the failed datasets
  - Datasets: This section contains the details of errors for each of the datasets

Datasets
--------
Datasets provide general information and details for each of datasets with errors

  - Id: Pennsieve Discover Id of the reported dataset
  - DOI: DOI of the reported dataset
  - Version: Version of the reported dataset
  - Name: Name/title of the reported dataset.
  - Errors: List of general/Non file related errors found in the reported datasets, visit the `Errors`_ section for more details.
  - ObjectErrors: List of errors found in the objects lists such as missing files, incorrect annotations and etc, visit the `ObjectErrors`_ section for more details.

.. _Errors:

Errors
------
This section provide some details on each of the errors

Scaffold found in objects list but the dataset is not tagged with scaffold (types.item.name)
````````````````````````````````````````````````````````````````````````````````````````````
The dataset type is not set to scaffold but it contains one or more scaffolds in the object lists. This does not neccessarily indicates an error in the dataset.

Dataset is tagged with scaffold (types.item.name) but no scaffold can be found in the list of objects
`````````````````````````````````````````````````````````````````````````````````````````````````````
The dataset type is set to scaffold but no scaffold annotation can be found in the dataset, this may indicate an error in the manifest file or the type of the dataset is incorrect.

Contextual Information cannot be found while scaffold is present
````````````````````````````````````````````````````````````````
Contextual Information providing details of the data such as scaffold cannot be found in the dataset despite the presence of a scaffold.
In short, a file with the additional mimetype - application/x.vnd.abi.context-information+json is missing.
Action: Check if a file annotated with contextual information is present in the manifest file. Check if the search engine is up-to-date.

.. _ObjectErrors:

ObjectErrors
------------
The object errors list provide the details of errors found in the dataset's objects list. These errors generally indicate there are problems in the file path or annotations.

ThumbnailError: Thumbnail not found in isSourceOf
`````````````````````````````````````````````````
This error occurs when the file is one of the following types::

 application/x.vnd.abi.scaffold.view+json
 application/x.vnd.abi.scaffold.meta+json
 text/vnd.abi.plot+tab-separated-values
 text/vnd.abi.plot+csv
Cause of the error: None of the files in the isSourceOf field of this file entry in the manifest has the mimetype - "inode/vnd.abi.plot+thumbnail".
Action: Check the manifest and make sure thumbnail entries are correctly annotated and added to the isSourceOf field of the corresponding file.

ThumbnailError: Missing isSourceOf entry
````````````````````````````````````````
This error occurs when the file is one of the following types::

 application/x.vnd.abi.scaffold.view+json
 application/x.vnd.abi.scaffold.meta+json
 text/vnd.abi.plot+tab-separated-values
 text/vnd.abi.plot+csv
Cause of the error: The entry of this file in the manifest does not have any entry or the entry is absent in the isSourceOf field.
Action: Check the manifest and make sure isSourceOf contains a valid thumbnail entry.

Reason: An error occurred (404) when calling the HeadObject operation: Not Found
````````````````````````````````````````````````````````````````````````````````
The file specified in path cannot be found in the data storage. This is either an error on the manifest or the search engine is returing out-of-sync information.
In some cases, the file name in the data storage may have been altered causing this issue.
Action: Check the manifest, make sure the path is specified correctly. Check the files and folders in the datset.

Reason: Cannot find the path
`````````````````````````````
The file stated in the RelativePath cannot be found, this may indicate a manifest error or the search engine contains incorrect information.
In some cases, the file name in the data storage may have been altered causing this issue.

Reason: Encounter a problem while looking for path
``````````````````````````````````````````````````
A problem has occurs while looking for the path specified in RelativePath.

Reason: Invalid response
````````````````````````
An error on the data storage, this may or may not be an error on the manifest and search engine. Check future reports for updates..
