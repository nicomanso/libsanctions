import os

DATA_PATH = os.environ.get('DATA_PATH', '.')
DATABASE_URI = 'sqlite:///data.sqlite'
DATABASE_URI = os.environ.get('DATABASE_URI') or DATABASE_URI

AWS_ACCESS_KEY_ID = os.environ.get('MORPH_AWS_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')  # noqa
AWS_SECRET_ACCESS_KEY = os.environ.get('MORPH_AWS_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')  # noqa
AWS_BUCKET = os.environ.get('AWS_BUCKET', 'data.opensanctions.org')
