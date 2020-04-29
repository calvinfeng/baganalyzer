import os
import pandas as pd

from baganalytics import BagLoader
from baganalytics import load_fmcl_localization_data, visualize_coordinates

# Logging
import logging
logging.basicConfig(level=logging.INFO)


DATA_DIR = 'bags'


def download():
    session = boto3.Session(profile_name='fetchcore-production')
    loader = BagLoader(session, 'arrow-rt.fetchcore-cloud.com')
    keys = loader.list_keys(robot='freight100-1173', action='navigate', num_keys=10)
    logger.info('successfully fetched %s keys, now proceeding to download' % len(keys))
    bags = loader.download_bags(keys, data_dir='bags')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    
    filepaths = []
    for f in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, f)
        if os.path.isfile(path):
            filepaths.append(path)

    logger.info('found %s bags in directory %s' % (len(filepaths), DATA_DIR))
    
    dfs = []
    for path in filepaths:
        df = load_fmcl_localization_data(path)
        if df is not None:
            dfs.append(df)

    final_df = pd.concat(dfs, axis=0)
    visualize_coordinates(final_df)
