import pandas as pd
import rosbag

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import logging
logger = logging.getLogger(__name__)


def load_fmcl_localization_data(filepath):
    """Extract localization status data from a bag file into DataFrame
    """
    try:
        bag = rosbag.Bag(filepath)   
    except rosbag.bag.ROSBagUnindexedException:
        logger.warn('%s is unindexed' % filepath)
        return None

    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_status']):
        secs = msg.header.stamp.secs
        nsecs = msg.header.stamp.nsecs
        valid = msg.localization_valid
        legacy_score = msg.legacy_localization_score
        patch_map_score = msg.patch_map_score

        rows.append(
            pd.DataFrame([
                [secs, nsecs, valid, legacy_score, patch_map_score]
            ], columns=['secs', 'nsecs', 'localization_valid', 'legacy_localization_score', 'patch_map_score'])
        )
    
    if len(rows) == 0:
        logger.warn('cannot find any localization status data from %s because len=0' % filepath)
        return None

    # Change index to date time object
    # Example: pd.Timestamp(1513393355, unit='s', tz='America/Los_Angeles')
    localization_status_df = pd.concat(rows, ignore_index=True)
    localization_status_df.index = pd.to_datetime(
        localization_status_df['secs']*10**9 + localization_status_df['nsecs'], unit='ns')

    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_score']):
        secs = msg.header.stamp.secs
        nsecs = msg.header.stamp.nsecs
        x = msg.pose.position.x
        y = msg.pose.position.y
        importance = msg.scores.importance
        likelihood = msg.scores.likelihood
        clear = msg.scores.clear
        dynamic = msg.scores.dynamic
        rows.append(
            pd.DataFrame([
                [secs, nsecs, x, y, importance, likelihood, clear, dynamic]
            ], columns=['secs', 'nsecs', 'x', 'y', 'importance', 'likelihood', 'clear', 'dynamic'])
        )

    # Change index to date time object
    # Example: pd.Timestamp(1513393355, unit='s', tz='America/Los_Angeles')
    localization_score_df = pd.concat(rows, ignore_index=True)
    localization_score_df.index = pd.to_datetime(
        localization_score_df['secs']*10**9 + localization_score_df['nsecs'], unit='ns')

    # Merge the two DF
    return pd.concat([localization_status_df,localization_score_df], axis=1)


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