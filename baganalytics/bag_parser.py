import pandas as pd
import rosbag

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import logging
logger = logging.getLogger(__name__)


def load_fmcl_localization_data(filename):
    """Extract localization status data from a bag file into DataFrame
    """
    try:
        bag = rosbag.Bag(filename)   
    except rosbag.bag.ROSBagUnindexedException:
        logger.warn('%s is unindexed' % filename)
        return None

    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_status']):
        timestamp = msg.header.stamp.secs + msg.header.stamp.nsecs * 10**-9 # Use numpy for higher precision
        valid = msg.localization_valid
        score = msg.legacy_localization_score

        rows.append(
            pd.DataFrame([
                [timestamp, valid, score]
            ], columns=['timestamp', 'localization_valid', 'legacy_localization_score'])
        )
    
    if len(rows) == 0:
        logger.warn('cannot find any localization status data from %s because len=0' % filename)
        return None

    localization_status_df = pd.concat(rows, ignore_index=True)
    localization_status_df.index = localization_status_df['timestamp']

    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_score']):
        timestamp = msg.header.stamp.secs + msg.header.stamp.nsecs * 10**-9 # Use numpy for higher precision
        x = msg.pose.position.x
        y = msg.pose.position.y
        importance = msg.scores.importance
        likelihood = msg.scores.likelihood
        clear = msg.scores.clear
        dynamic = msg.scores.dynamic
        rows.append(
            pd.DataFrame([
                [timestamp, x, y, importance, likelihood, clear, dynamic]
            ], columns=['timestamp', 'x', 'y', 'importance', 'likelihood', 'clear', 'dynamic'])
        )

    localization_score_df = pd.concat(rows, ignore_index=True)
    localization_score_df.index = localization_score_df['timestamp']

    # Merge the two DF
    return pd.concat([localization_status_df,localization_score_df], axis=1)


def visualize_coordinates(df):
    ax = plt.axes(projection='3d')
    ax.scatter3D(
        df['x'].to_numpy(),
        df['y'].to_numpy(),
        df['likelihood'].to_numpy(), c='gray',
                                     label='likelihood')
    ax.scatter3D(
        df['x'].to_numpy(),
        df['y'].to_numpy(),
        df['importance'].to_numpy(), c='orange',
                                     label='importance')
    ax.scatter3D(
        df['x'].to_numpy(),
        df['y'].to_numpy(),
        df['legacy_localization_score'].to_numpy(), c='red',
                                                    label='legacy_localization_score')

    ax.set_xlabel('x')  
    ax.set_ylabel('y')
    ax.set_zlabel('localization score value unnormalized')
    ax.set_title('coordinate vs localization health')
    plt.legend()
    plt.show()
