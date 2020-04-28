import os
import rosbag


class S3BagLoader(object):
    def __init__(self, boto3_session, instance, bucket='production-bag-file-collections'):
        self.s3 = boto3_session.client('s3')
        self.bucket = bucket
        self.instance = instance

    def list_keys(self, robot, action):
        more = True
        
        keys = []
        continuation_token = ''
        while more:
            kwargs = {
                'Bucket': self.bucket,
                'Prefix': os.path.join(self.instance, robot, action),
                'MaxKeys': 1000,
            }

            if continuation_token != '':
                kwargs['ContinuationToken'] = continuation_token

            resp = self.s3.list_objects_v2(**kwargs)
            for obj in resp['Contents']:
                keys.append(obj['Key'])

            more = resp['IsTruncated']
            if more:
                continuation_token = resp['NextContinuationToken']

        return keys
    

    def load_bag(self, key, filename='temporary.bag', remove=True):
        with open(filename, 'wb') as f:
            self.s3.download_fileobj(self.bucket, key, f)

        bag = rosbag.Bag(filename)
        if remove:
            os.remove(filename)

        return  bag