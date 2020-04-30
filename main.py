import os
import boto3
import pandas as pd
import pdb

from baganalytics import BagLoader
from baganalytics import load_fmcl_localization_data, visualize_coordinates

# Logging
import logging
logging.basicConfig(level=logging.INFO)


DATA_DIR = 'bags'


def download_nav_bags(instance, robots=[]):
    session = boto3.Session(profile_name='fetchcore-production')

    loader = BagLoader(session, instance)
    for robot in robots:
        keys = loader.list_keys(robot=robot, action='navigate', num_keys=20)
        logger.info('successfully fetched %s keys, now proceeding to download' % len(keys))
        bags = loader.download_bags(keys, data_dir=DATA_DIR)
        logger.info('successfully downloaded %s bags for %s' % (len(bags), robot))

    

if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    #download_nav_bags('arrow-rt.fetchcore-cloud.com',
    #    robots=['freight100-1173', 'freight100-1279', 'freight100-1396', 'freight100-1397'])

    filepaths = []
    for f in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, f)
        if os.path.isfile(path):
            filepaths.append(path)

    logger.info('found %s bags in directory %s' % (len(filepaths), DATA_DIR))
    
    dfs = []
    for path in filepaths:
        logger.info('loading %s into data frame' % path)
        df = load_fmcl_localization_data(path)
        if df is not None:
            dfs.append(df)

    final_df = pd.concat(dfs, axis=0)
    
    # Resample returns a DateTimeIndexSampler, it needs an aggregate function to convert it back
    # into a DataFrame
    final_df = final_df.resample('1S') .mean()
    visualize_coordinates(final_df, columns=['patch_map_score'])

    final_df.to_csv('localization_scores.csv')
    