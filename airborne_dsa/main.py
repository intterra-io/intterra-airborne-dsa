"""Main file"""

from datetime import datetime
import sys
import glob
import os
import time
import re
import boto3

s3 = boto3.client("s3")  # TODO: pass keys from json config (optionally)


def main():
    """
    Main func
    """

    # print(config)

    raise NotImplementedError

    # init
    bucket = config["bucket"]  # TODO: Convert to persistant .json config
    now = datetime.utcnow()
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Get current working directory (CWD) and mission name from args
    mission_name, mission_timestamp, mission_file_path = find_mission()
    if mission_name == None:
        mission_name = get_mission_from_input()
        create_mission(mission_name, bucket)
    else:
        answer = ""
        while answer != "yes" and answer != "no":
            print(
                f'Use current mission (yes/no): "{mission_name}" from {mission_timestamp.ctime()}?'
            )
            answer = sys.stdin.readline().rstrip("\n").rstrip("\n")
        if answer == "no":
            mission_name = get_mission_from_input()
            os.remove(mission_file_path)
            create_mission(mission_name, bucket)

    # listen for files
    print(
        f'Listening for files in mission "{mission_name}" at {now.ctime()} UTC in bucket "{bucket}"...'
    )
    print("(CTRL + C to exit)")
    while True:
        upload_kmls(mission_name, dir_path, bucket)
        upload_tifs(mission_name, dir_path, bucket)
        time.sleep(15)


def get_mission_from_input():
    name = ""
    while not re.match(r"^[0-9a-z]+$", name, re.IGNORECASE):
        print("Please enter mission name (alphanumeric): ")
        name = sys.stdin.readline().rstrip("\n").rstrip("\n")
    return name


def create_mission(mission_name, bucket):
    # create mission
    now = datetime.utcnow()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    mission_file_name = (
        f'{mission_name}_{now.strftime("%Y%m%d")}_{now.strftime("%H%M")}Z.txt'
    )
    mission_path = f"{dir_path}/{mission_file_name}"
    with open(mission_path, "w+") as f:
        f.write("")
    s3.upload_file(mission_path, bucket, f"MISSION/{mission_file_name}")
    time.sleep(1)


def find_mission():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for file_path in glob.iglob(f"{dir_path}/*.txt", recursive=False):
        file_name = os.path.basename(file_path)
        m = re.match(
            r"([a-z0-9]+)_([0-9]{8})_([0-9]{4})z\.txt", file_name, re.IGNORECASE
        )
        if m != None:
            mission_timestamp = datetime.strptime(
                f"{m.group(2)}{m.group(3)}", "%Y%m%d%H%M"
            )
            return (m.group(1), mission_timestamp, file_name)
    return None, None, None


def upload_kmls(mission_name, path, bucket):
    # find KMLs (eg: 20200831_193612Z_Crawl1_IntenseHeat.kml)
    for file_path in glob.iglob(f"{path}/*.kml", recursive=False):
        now = datetime.utcnow()
        new_obj = f'TACTICAL/{now.strftime("%Y%m%d")}_{now.strftime("%H%M%S")}Z_{mission_name}_IntenseHeat.kml'
        print(f"Uploading {file_path} to {new_obj}...")

        # Strip points with regex
        with open(file_path, "r+") as f:
            contents = f.read()
            with open(file_path, "w") as f:
                modified_contents = re.sub(
                    r"<Point>[-.\n\t<>a-z0-9,\/]+<\/Point>",
                    "",
                    contents,
                    flags=re.MULTILINE,
                )
                f.write(modified_contents)

        s3.upload_file(file_path, bucket, new_obj)
        os.remove(file_path)
        print("done!")
        time.sleep(1)


def upload_tifs(mission_name, path, bucket):
    # find IRs (eg: 20200818_031612Z_Crawl1_IRimage.tif)
    for file_path in glob.iglob(f"{path}/*.tif", recursive=False):
        now = datetime.utcnow()
        new_obj = f'IMAGERY/{now.strftime("%Y%m%d")}_{now.strftime("%H%M%S")}Z_{mission_name}_IRimage.tif'
        print(f"Uploading {file_path} to {new_obj}...")
        s3.upload_file(file_path, bucket, new_obj)
        os.remove(file_path)
        print("done!")
        time.sleep(1)

    for file_path in glob.iglob(f"{path}/*.tiff", recursive=False):
        now = datetime.utcnow()
        new_obj = f'IMAGERY/{now.strftime("%Y%m%d")}_{now.strftime("%H%M%S")}Z_{mission_name}_IRimage.tif'
        print(f"Uploading {file_path} to {new_obj}...")
        s3.upload_file(file_path, bucket, new_obj)
        os.remove(file_path)
        print("done!")
        time.sleep(1)


if __name__ == "__main__":
    main()
