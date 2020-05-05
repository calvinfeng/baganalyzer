import os
import boto3
import pandas as pd
import pdb

from baganalytics import BagLoader
from baganalytics import load_fmcl_localization_data, visualize_coordinates, load_battery_data

# Logging
import logging
logging.basicConfig(level=logging.INFO)


RAW_DATA_DIR = 'bags'
PROCESSED_DATA_DIR = 'processed_data'

def download_nav_bags(instance, robots=[], num_bags_per_robot=100):
    session = boto3.Session(profile_name='fetchcore-production')

    loader = BagLoader(session, instance)
    for robot in robots:
        keys = loader.list_keys(robot=robot, action='navigate', num_keys=num_bags_per_robot)
        logger.info('successfully fetched %s keys, now proceeding to download' % len(keys))
        bags = loader.download_bags(keys, data_dir=os.path.join(RAW_DATA_DIR, instance))
        logger.info('successfully downloaded %s bags for %s' % (len(bags), robot))


def localization_analytics():
    logger = logging.getLogger(__name__)

    # instance = 'arrow-rt.fetchcore-cloud.com'
    # robots = ['freight100-1173', 'freight100-1279', 'freight100-1396', 'freight100-1397']
    instance = 'ge-selmer.fetchcore-cloud.com'
    robots = ['freight100-1242', 'freight100-1369']
    download_nav_bags(instance, robots=robots, num_bags_per_robot=50)

    filepaths = []
    for f in os.listdir(os.path.join(RAW_DATA_DIR, instance)):
        path = os.path.join(RAW_DATA_DIR, instance, f)
        if os.path.isfile(path):
            filepaths.append(path)

    logger.info('found %s bags in directory %s' % (len(filepaths), os.path.join(RAW_DATA_DIR, instance)))
    
    dfs = []
    for path in filepaths:
        logger.info('loading %s into data frame' % path)
        df = load_fmcl_localization_data(path)
        if df is not None:
            dfs.append(df)

    final_df = pd.concat(dfs, axis=0).dropna()
    final_df["localization_valid"] = final_df["localization_valid"].astype(int)
    
    # Resample returns a DateTimeIndexSampler, it needs an aggregate function to convert it back
    # into a DataFrame
    final_df = final_df.resample('1S') .mean()
    visualize_coordinates(final_df, columns=['patch_map_score'])

    output_dir = os.path.join(PROCESSED_DATA_DIR, instance)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    final_df.to_csv(os.path.join(output_dir, 'localization_score_1_sec_interval.csv'))


def battery_analytics():
    instance = 'ge-selmer.fetchcore-cloud.com'

    filepaths = []
    for f in os.listdir(os.path.join(RAW_DATA_DIR, instance)):
        path = os.path.join(RAW_DATA_DIR, instance, f)
        if os.path.isfile(path):
            filepaths.append(path)

    for path in filepaths:
        load_battery_data(path)


if __name__ == '__main__':
    battery_analytics()
