import os
import rosbag
import StringIO 
import logging


logger = logging.getLogger(__name__)


class BagLoader(object):
    def __init__(self, boto3_session, instance, bucket='production-bag-file-collections'):
        self.s3 = boto3_session.client('s3')
        self.bucket = bucket
        self.instance = instance

    def list_keys(self, robot, action, num_keys=100):
        """List all the keys for a specific robot and action.
        TODO: Don't fetch everything, just fetch the number of specified keys
        """
        more = True
        
        keys = []
        continuation_token = None
        while more:
            kwargs = {
                'Bucket': self.bucket,
                'Prefix': os.path.join(self.instance, robot, action),
                'MaxKeys': 1000,
            }

            if continuation_token is not None:
                kwargs['ContinuationToken'] = continuation_token

            resp = self.s3.list_objects_v2(**kwargs)
            for obj in resp['Contents']:
                keys.append(obj['Key'])

            more = resp['IsTruncated']
            if more:
                continuation_token = resp['NextContinuationToken']

        return keys[-num_keys:]

    def download_bags(self, keys, data_dir='bags'):
        """Downloads a list of bags to a specified data directory.

        wb	Opens a file for writing only in binary format.
        w+	Opens a file for both writing and reading.
        wb+	Opens a file for both writing and reading in binary format.
        """
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        downloaded_bag_paths = []
        for key in keys:
            parts = key.split('/')
            filename = parts[len(parts)-1]
            path = os.path.join(data_dir, filename)
            if os.path.exists(path):
                logger.info('%s already exists, no need to download' % path)
                downloaded_bag_paths.append(path)
                continue

            logger.info('downloading %s' % filename)
            with open(path, 'wb') as f:
                self.s3.download_fileobj(self.bucket, key, f)
            logger.info('completed download for %s' % filename)
            downloaded_bag_paths.append(path)
        
        return downloaded_bag_paths
    
    def load_bag(self, key, filename='temporary.bag', remove=True):
        """Experimental
        """
        with open(filename, 'wb') as f:
            self.s3.download_fileobj(self.bucket, key, f)

        print 'Completed downloading to file'
        bag = rosbag.Bag(filename)
        if remove:
            os.remove(filename)

        return bag

    def load_bag_in_mem(self, key):
        """Experimental
        """
        resp = self.s3.get_object(Bucket=self.bucket, Key=key)
        bag = rosbag.Bag(resp['Body'].read())
        return bag