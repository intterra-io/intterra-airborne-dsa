#!/usr/bin/env python3

# README
# pip install awscli
# aws configure

import boto3
from botocore.config import Config
from datetime import datetime
import sys
import glob
import os
import time
import json  
import re
from signal import signal, SIGINT
f = open('config.json')
config = json.load(f)
aws_config = Config(
    region_name = 'us-west-1'
)
s3_with_creds = boto3.client(
    's3', 
    config=aws_config, 
    aws_secret_access_key=config['aws_secret_access_key'], 
    aws_access_key_id=config['aws_access_key_id']
) 
s3_without_creds = boto3.client(
    's3', 
    config=aws_config
)
s3 = s3_with_creds if config['aws_secret_access_key'] and config['aws_access_key_id'] else s3_without_creds


def run():
    # init
    bucket = config['bucket']
    now = datetime.utcnow()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    welcome()

    # Get current working directory (CWD) and mission name from args
    mission_name, mission_timestamp, mission_file_path = find_mission()
    if mission_name == None:
        mission_name = get_mission_from_input()
        create_mission(mission_name, bucket)
    else:
        answer = ''
        while answer != 'yes' and answer != 'no':
            print(
                f'Use current mission (yes/no): "{mission_name}" from {mission_timestamp.ctime()}?')
            answer = sys.stdin.readline().rstrip('\n').rstrip('\n')
        if answer == 'no':
            mission_name = get_mission_from_input()
            os.remove(mission_file_path)
            create_mission(mission_name, bucket)

    # listen for files
    print(
        f'Listening for files in mission "{mission_name}" at {now.ctime()} UTC in bucket "{bucket}"...')
    print('(CTRL + C to exit)')
    while True:
        upload_kmls(mission_name, dir_path, bucket)
        upload_tifs(mission_name, dir_path, bucket)
        time.sleep(15)


def get_mission_from_input():
    name = ''
    while not re.match(r'^[0-9a-z]+$', name, re.IGNORECASE):
        print('Please enter mission name (alphanumeric): ')
        name = sys.stdin.readline().rstrip('\n').rstrip('\n')
    return name


def create_mission(mission_name, bucket):
    # create mission
    now = datetime.utcnow()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    mission_file_name = f'{mission_name}_{now.strftime("%Y%m%d")}_{now.strftime("%H%M")}Z.txt'
    mission_path = f'{dir_path}/{mission_file_name}'
    try:
        with open(mission_path, 'w+') as f:
            f.write('')
        s3.upload_file(mission_path, bucket, f'MISSION/{mission_file_name}')
        time.sleep(1)
    except Exception as e:
        os.remove(mission_path)
        raise e


def find_mission():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for file_path in glob.iglob(f'{dir_path}/*.txt', recursive=False):
        file_name = os.path.basename(file_path)
        m = re.match(
            r'([a-z0-9]+)_([0-9]{8})_([0-9]{4})z\.txt', file_name, re.IGNORECASE)
        if m != None:
            mission_timestamp = datetime.strptime(
                f'{m.group(2)}{m.group(3)}', '%Y%m%d%H%M')
            return (m.group(1), mission_timestamp, file_name)
    return None, None, None


def upload_kmls(mission_name, path, bucket):
    # find KMLs (eg: 20200831_193612Z_Crawl1_IntenseHeat.kml)
    for file_path in glob.iglob(f'{path}/*.kml', recursive=False):

        now = datetime.utcnow()
        new_obj = f'TACTICAL/{now.strftime("%Y%m%d")}_{now.strftime("%H%M%S")}Z_{mission_name}_IntenseHeat.kml'
        print(f'Uploading {file_path} to {new_obj}...')

        # Strip points with regex
        with open(file_path, 'r+') as f:
            contents = f.read()
            with open(file_path, 'w') as f:
                modified_contents = re.sub(
                    r'<Point>[-.\n\t<>a-z0-9,\/]+<\/Point>', '', contents, flags=re.MULTILINE)
                f.write(modified_contents)

        s3.upload_file(file_path, bucket, new_obj)
        os.remove(file_path)
        print('done!')
        time.sleep(1)


def upload_tifs(mission_name, path, bucket):
    # find IRs (eg: 20200818_031612Z_Crawl1_IRimage.tif)
    for file_path in glob.iglob(f'{path}/*.tif', recursive=False):
        now = datetime.utcnow()
        new_obj = f'IMAGERY/{now.strftime("%Y%m%d")}_{now.strftime("%H%M%S")}Z_{mission_name}_IRimage.tif'
        print(f'Uploading {file_path} to {new_obj}...')
        s3.upload_file(file_path, bucket, new_obj)
        os.remove(file_path)
        print('done!')
        time.sleep(1)

    for file_path in glob.iglob(f'{path}/*.tiff', recursive=False):
        now = datetime.utcnow()
        new_obj = f'IMAGERY/{now.strftime("%Y%m%d")}_{now.strftime("%H%M%S")}Z_{mission_name}_IRimage.tif'
        print(f'Uploading {file_path} to {new_obj}...')
        s3.upload_file(file_path, bucket, new_obj)
        os.remove(file_path)
        print('done!')
        time.sleep(1)


def welcome():
    print("   _____  .__      ___.                                ________    _________   _____   ")
    print("  /  _  \\ |__|_____\\_ |__   ___________  ____   ____   \\______ \\  /   _____/  /  _  \\  ")
    print(" /  /_\\  \\|  \\_  __ \\ __ \\ /  _ \\_  __ \\/    \\_/ __ \\   |    |  \\ \\_____  \\  /  /_\\  \\ ")
    print("/    |    \\  ||  | \\/ \\_\\ (  <_> )  | \\/   |  \\  ___/   |    `   \\/        \\/    |    \\")
    print("\\____|__  /__||__|  |___  /\\____/|__|  |___|  /\\___  > /_______  /_______  /\\____|__  /")
    print("        \\/              \\/                  \\/     \\/          \\/        \\/         \\/ ")
    print("Airborne API Data Shipping App powered by Intterra")
    print('\n')
    print("Follow the prompts to create a mission file name or select an existing mission. After selecting a mission, move the files you would like to upload into this folder. For images, upload a .tif or .tiff file. For map features, upload a .kml file.")
    print('\n')


def handler(signal_received, frame):
    print('Goodbye!')
    sys.exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    run()
