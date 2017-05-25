import os

DATA_PATH = os.environ.get('DATA_PATH', '.')
DATABASE_URI = 'sqlite:///data.sqlite'
DATABASE_URI = os.environ.get('DATABASE_URI') or DATABASE_URI

BUCKET = os.environ.get('AWS_BUCKET', 'data.opensanctions.org')
