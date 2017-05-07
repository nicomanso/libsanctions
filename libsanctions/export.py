import os
import logging
from unicodecsv import DictWriter

from libsanctions.config import DATA_PATH
from libsanctions.model import session

log = logging.getLogger(__name__)


def export_csv_table(model, name):
    export_path = os.path.join(DATA_PATH, 'exports')
    try:
        os.makedirs(export_path)
    except:
        pass

    file_path = os.path.join(export_path, '%s.csv' % name)
    log.info("Exporting to %s...", file_path)
    writer = None
    with open(file_path, 'w') as fh:
        for obj in session.query(model):
            row = obj.to_row()
            if writer is None:
                writer = DictWriter(fh, row.keys())
                writer.writeheader()
            writer.writerow(row)

    if writer is None:
        os.unlink(file_path)
        return None

    return file_path
