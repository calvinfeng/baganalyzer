import StringIO
import boto3
import rosbag
import pandas as pd
import os
from s3_bag_loader import S3BagLoader


BUCKET = 'production-bag-file-collections'
KEY = 'arrow-rt.fetchcore-cloud.com/freight100-1173/navigate/2020-04-23-09-38-55.614703_task-76202_action-255687_freight100-1173_0.bag'


def temp():
    session = boto3.Session(profile_name='fetchcore-production')
    s3 = session.client('s3')
    
    with open('temp.bag', 'wb') as f:
        print 'Downloading object from S3'
        s3.download_fileobj(BUCKET, KEY, f)

    
    bag = rosbag.Bag('temp.bag')   

    df_rows = []
    for topic, msg, time in bag.read_messages(topics=['/fmcl/pose']):
        df_rows.append(
            pd.DataFrame([
                [time, msg.pose.pose.position.x, msg.pose.pose.position.y]
            ], columns=['time', 'x', 'y'])
        )

    position_df = pd.concat(df_rows, ignore_index=True)
    position_df.index = position_df['time']
    print position_df
    
    bag.close()
    os.remove("temp.bag")


"""
wb	Opens a file for writing only in binary format.
w+	Opens a file for both writing and reading.
wb+	Opens a file for both writing and reading in binary format.
"""
if __name__ == '__main__':
    session = boto3.Session(profile_name='fetchcore-production')

    loader = S3BagLoader(session, 'arrow-rt.fetchcore-cloud.com')
    keys = loader.list_keys(robot='freight100-1173', action='navigate')
    print 'Successfully fetched %s keys' % len(keys)
    print 'last key %s' % keys[len(keys)-1]

    bag = loader.load_bag(keys[len(keys)-1])
    topics = bag.get_type_and_topic_info()[1].keys()
    for topic in topics:
        print topic
    bag.close()