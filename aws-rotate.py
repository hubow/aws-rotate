#!/usr/bin/env python

"""
Script to make the rotation of AWS Access and Secret Keys easier.
"""

import os
import boto3
import argparse
from configparser import ConfigParser
from shutil import copyfile

def get_credentials_file():
    return os.path.expanduser(os.getenv('AWS_SHARED_CREDENTIALS_FILE', '~/.aws/credentials'))

def backup_credentials(credentials_file):
    copyfile(credentials_file, '{}.bkp'.format(credentials_file))
    print('Backup file created - {}.bkp'.format(credentials_file))

def get_credentials_list(credentials_file):
    credentials = ConfigParser()
    if credentials_file not in credentials.read(credentials_file):
        raise ConfigException('Unable to read AWS credentials file.')
    return credentials

def get_current_credentials(credentials_list, aws_profile):
    return credentials_list[aws_profile]['aws_access_key_id']

def create_new_keys(aws_profile):
    session = boto3.session.Session(profile_name=aws_profile)
    iam = session.client('iam')
    new_keys = iam.create_access_key()['AccessKey']
    return {
        'AccessKeyId': new_keys['AccessKeyId'], 
        'SecretAccessKey': new_keys['SecretAccessKey']
    }

def write_new_credentials(credentials_list, credentials_file):
    with open(credentials_file, 'w') as aws_credentials_file:
        credentials_list.write(aws_credentials_file)
    return True

def delete_old_key(aws_profile, old_access_key):
    session = boto3.session.Session(profile_name=aws_profile)
    iam = session.client('iam')
    iam.delete_access_key(AccessKeyId=old_access_key)
    print('Old AWS Access Key was deleted from IAM')
    return True

def parse_args(prog='aws-rotate',formatter_class=argparse.ArgumentDefaultsHelpFormatter):
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
    new_access_key = create_new_keys(aws_profile)
    credentials_list.set(aws_profile, 'aws_access_key_id', new_access_key['AccessKeyId'])
    credentials_list.set(aws_profile, 'aws_secret_access_key', new_access_key['SecretAccessKey'])
    write_new_credentials(credentials_list, credentials_file)
    delete_old_key(aws_profile, current_access_key)

if __name__ == '__main__':
    rotate_keys()
