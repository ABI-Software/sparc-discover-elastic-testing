import os


class Config(object):
    PENNSIEVE_API_HOST = os.environ['PENNSIEVE_API_HOST']
    # PENNSIEVE_API_SECRET = os.environ['PENNSIEVE_API_SECRET']
    # PENNSIEVE_API_TOKEN = os.environ['PENNSIEVE_API_TOKEN']
    BIOLUCIDA_ENDPOINT = os.environ.get("BIOLUCIDA_ENDPOINT", "https://sparc.biolucida.net/api/v1")
    SCICRUNCH_API_HOST = os.environ['SCICRUNCH_API_HOST']
    SCICRUNCH_API_KEY = os.environ['SCICRUNCH_API_KEY']
    SCICRUNCH_API = os.environ.get('SCICRUNCH_API', 'https://scicrunch.org/api/1')
    # SPARC_PENNSIEVE_ORGANISATION_ID = 367
    # ALGOLIA_KEY=os.environ['ALGOLIA_KEY']
    # ALGOLIA_ID=os.environ['ALGOLIA_ID']
    # ALGOLIA_INDEX=os.environ['ALGOLIA_INDEX']
    # AWS_KEY=os.environ['AWS_KEY']
    # AWS_SECRET=os.environ['AWS_SECRET']
