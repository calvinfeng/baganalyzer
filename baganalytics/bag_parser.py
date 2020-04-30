import pandas as pd
import rosbag
import pdb
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import logging
logger = logging.getLogger(__name__)


def _get_localization_status_df(bag):
    timestamps = []
    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_status']):
        timestamps.append(msg.header.stamp.secs*10**9 + msg.header.stamp.nsecs)
        valid = msg.localization_valid
        legacy_score = msg.legacy_localization_score
        patch_map_score = msg.patch_map_score

        rows.append(
            pd.DataFrame([
                [valid, legacy_score, patch_map_score]
            ], columns=['localization_valid', 'legacy_localization_score', 'patch_map_score'])
        )
    
    if len(rows) == 0:
        logger.warn('cannot find any localization status data from %s because len=0' % filepath)
        raise ValueError('localization status data is empty')

    return pd.concat(rows, ignore_index=True), np.array(timestamps)


def _get_localization_score_df(bag):
    timestamps = []
    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_score']):
        timestamps.append(msg.header.stamp.secs*10**9 + msg.header.stamp.nsecs)
        x = msg.pose.position.x
        y = msg.pose.position.y
        importance = msg.scores.importance
        likelihood = msg.scores.likelihood
        clear = msg.scores.clear
        dynamic = msg.scores.dynamic
        rows.append(
            pd.DataFrame([
                [x, y, importance, likelihood, clear, dynamic]
            ], columns=['x', 'y', 'importance', 'likelihood', 'clear', 'dynamic'])
        )

    if len(rows) == 0:
        logger.warn('cannot find any localization score data from %s because len=0' % filepath)
        raise ValueError('localization score data is empty')

    return pd.concat(rows, ignore_index=True), np.array(timestamps)


def load_fmcl_localization_data(filepath):
    """Extract localization status data from a bag file into DataFrame
    """
    try:
        bag = rosbag.Bag(filepath)   
    except rosbag.bag.ROSBagUnindexedException:
        logger.warn('%s is unindexed' % filepath)
        return None

    loc_status_df, loc_status_ts = _get_localization_status_df(bag)
    loc_score_df, loc_score_ts = _get_localization_score_df(bag)

    are_timestamps_aligned = False
    # There is a possibility one of the topic is missing a message or two.
    if loc_status_ts.size > loc_score_ts.size:
        delta = loc_status_ts.size - loc_score_ts.size
        loc_status_ts = loc_status_ts[:-delta]
    elif loc_status_ts.size < loc_score_ts.size:
        delta = loc_score_ts.size - loc_status_ts.size
        loc_score_ts = loc_score_ts[:-delta]

    if not np.isclose(loc_status_ts, loc_score_ts).all():
        raise ValueError('timestamps from two localization topics do not match')
    
    # Change index to date time object
    # Example: pd.Timestamp(1513393355, unit='s', tz='America/Los_Angeles')
    timestamp_df = pd.DataFrame(pd.to_datetime(loc_status_ts, unit='ns'), columns=['timestamp'])
    # Merge the two DF
    df = pd.concat([timestamp_df, loc_status_df, loc_score_df], axis=1)
    df.index = df['timestamp']
    df['hour'] = df['timestamp'].dt.hour
    return df


def visualize_coordinates(df, columns=['patch_map_score']):
    ax = plt.axes(projection='3d')

    for col in columns:
        ax.scatter3D(
            df['x'].to_numpy(),
            df['y'].to_numpy(),
            df[col].to_numpy(), label=col)

    ax.set_xlabel('x')  
    ax.set_ylabel('y')
    ax.set_zlabel('localization metrics')
    ax.set_title('Localization by Spatial Coordinate')
    plt.legend()
    plt.show()


def load_messages_helper(filepath):
    try:
        bag = rosbag.Bag(filepath)   
    except rosbag.bag.ROSBagUnindexedException:
        logger.warn('%s is unindexed' % filepath)
        return None

    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_status']):
        print msg