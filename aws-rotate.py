#!/usr/bin/env python

"""
Script to make the rotation of AWS Access and Secret Keys easier.
It doesn't validate number of existing IAM keys.
"""

import os
import boto3
import argparse
from configparser import ConfigParser
from shutil import copyfile
import time

def get_credentials_file():
    return os.path.expanduser(os.getenv('AWS_SHARED_CREDENTIALS_FILE', '~/.aws/credentials'))

def backup_credentials(credentials_file):
    """
    Backup the current credentials file with a .bkp extension
    """
    copyfile(credentials_file, '{}.bkp'.format(credentials_file))
    print('Backup file created - {}.bkp'.format(credentials_file))

def get_credentials_list(credentials_file):
    """
    Return the credentials file as a configparser object
    """
    credentials = ConfigParser()
    if credentials_file not in credentials.read(credentials_file):
        raise ConfigException('Unable to read AWS credentials file.')
    return credentials

def get_current_credentials(credentials_list, aws_profile):
    """
    Get the current Access Key
    """
    return credentials_list[aws_profile]['aws_access_key_id']

def secure_key(key):
    """
    Hide part of key while printing it out on screen
    """
    secured_key = '*****{}'.format(key[-5:])
    return secured_key

def create_new_keys(aws_profile):
    """
    Create a new pair of AWS keys
    """
    session = boto3.session.Session(profile_name=aws_profile)
    iam = session.client('iam')
    new_keys = iam.create_access_key()['AccessKey']
    print('[{}] New key created ({})'.format(aws_profile, secure_key(new_keys['AccessKeyId'])))
    return {
        'AccessKeyId': new_keys['AccessKeyId'], 
        'SecretAccessKey': new_keys['SecretAccessKey']
    }

def write_new_keys(credentials_list, credentials_file):
    """
    Write the AWS credentials config file
    """
    with open(credentials_file, 'w') as aws_credentials_file:
        credentials_list.write(aws_credentials_file)
    return True

def delete_old_key(aws_profile, old_access_key):
    """
    Delete the old access key from IAM. Retries 3 times, due the time required for AWS to let use new key.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            session = boto3.session.Session(profile_name=aws_profile)
            iam = session.client('iam')
            iam.delete_access_key(AccessKeyId=old_access_key)
            print('[{}] Old key was deleted from IAM ({})'.format(aws_profile, secure_key(old_access_key)))
            break
        except:
            if attempt > 3:
                break
        time.sleep(10)
    return True

def parse_args(prog='aws-rotate',formatter_class=argparse.ArgumentDefaultsHelpFormatter):
    """
    Check whether profile name is given
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile", help="Specify the AWS profile with --profile arg.", default=None)
    args = parser.parse_args()
    return args.profile

def rotate_keys():
    aws_profile = parse_args()
    credentials_file = get_credentials_file()
    backup_credentials(credentials_file)
    credentials_list = get_credentials_list(credentials_file)
    current_access_key = get_current_credentials(credentials_list, aws_profile)
    new_keys = create_new_keys(aws_profile)
    credentials_list.set(aws_profile, 'aws_access_key_id', new_keys['AccessKeyId'])
    credentials_list.set(aws_profile, 'aws_secret_access_key', new_keys['SecretAccessKey'])
    write_new_keys(credentials_list, credentials_file)
    delete_old_key(aws_profile, current_access_key)

if __name__ == '__main__':
    rotate_keys()
