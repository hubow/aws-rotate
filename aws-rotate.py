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

def get_credentials(credentials_file):
    credentials = ConfigParser()
    if credentials_file not in credentials.read(credentials_file):
        raise ConfigException('Unable to read AWS credentials file.')
    return credentials

def get_current_credentials(credentials_list, aws_profile):
    """
    Get the current Access Key in order to delete it from AWS
    """
    return credentials_list[aws_profile]['aws_access_key_id']

def parse_args(prog='aws-rotate',formatter_class=argparse.ArgumentDefaultsHelpFormatter):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile", help="Specify the AWS profile with --profile arg.", default = None)
    args = parser.parse_args()
    return args.profile

def rotate_keys():
    aws_profile = parse_args()
    credentials_file = get_credentials_file()
    backup_credentials(credentials_file)
    credentials_list = get_credentials(credentials_file)
    current_aws_access_key = get_current_credentials(credentials_list, aws_profile)

if __name__ == '__main__':
    rotate_keys()
