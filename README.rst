SciCrunch Knowledge Testing
===========================

This repository holds tests for the knowledge provided from SciCrunch endpoints.


Tests included:
---------------
SPARC Discover and SciCrunch Testing
------------------------------------
Datasets on Discover compared to the knowledge on SciCrunch.

Running the tests
-----------------
 python -m unittest discover -s /Users/hsor001/Projects/sparc/sparc-discover-elastic-testing/tests

Required Environment variables
------------------------------
The following environment variables need to be set to the appropriate values for the tests to run::

 PENNSIEVE_API_HOST
 PENNSIEVE_API_SECRET
 PENNSIEVE_API_TOKEN
 SCICRUNCH_API_HOST
 SCICRUNCH_API_KEY

Where *PENNSIEVE_API_HOST* could be set to *https://api.pennsieve.io/discover*, and *SCICRUNCH_API_HOST* could be set to *https://scicrunch.org/api/1/elastic/SPARC_PortalDatasets_dev*.
The other environment variables *PENNSIEVE_API_SECRET*, *PENNSIEVE_API_TOKEN*, and *SCICRUNCH_API_KEY* you will need to figure out for yourself.
