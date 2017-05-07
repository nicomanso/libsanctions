import logging
import warnings
from sqlalchemy import exc as sa_exc

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)

fmt = '[%(levelname)-8s] %(name)-12s: %(message)s'
logging.basicConfig(level=logging.INFO, format=fmt)
logging.getLogger('requests').setLevel(logging.WARNING)


from libsanctions.source import Source  # noqa
