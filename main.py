import rosbag
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pdb
import StringIO
import boto3


def export_to_csv(bag):
    df_rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/pose']):
        df_rows.append(
            pd.DataFrame([
                [time, msg.pose.pose.position.x, msg.pose.pose.position.y]
            ], columns=['time', 'x', 'y'])
        )

    position_df = pd.concat(df_rows, ignore_index=True)
    position_df.index = position_df['time']
    position_df.to_csv("fmcl_pose.csv", index=False)


def visualize_coordinates(bag):
    rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/localization_score']):
        rows.append(
            pd.DataFrame([
                [time, msg.pose.position.x, msg.pose.position.y, msg.scores.importance, msg.scores.likelihood]
            ], columns=['time', 'x', 'y', 'importance', 'likelihood'])
        )

    df = pd.concat(rows, ignore_index=True)
    df.index = df['time']

    ax = plt.axes(projection='3d')
    ax.scatter3D(df['x'].to_numpy(), df['y'].to_numpy(), df['likelihood'].to_numpy()+0.1, 'gray')
    ax.scatter3D(df['x'].to_numpy(), df['y'].to_numpy(), df['importance'].to_numpy(), 'red')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('likelihood or importance')
    ax.set_title('coordinate vs localization likelihood/importance')
    plt.show()


if __name__ == '__main__':
    filename = '2020-04-09-14-03-05.047358_task-68747_action-246476_freight100-1173_0.bag'
    bag = rosbag.Bag(filename)
    # visualize_coordinates(bag)
    
    for topic, msg, time in bag.read_messages(topics=['/fmcl/particle_cloud_debug']):
        print("=====================================================================")
        print msg

    bag.close()