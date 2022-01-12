#!/usr/bin/env python
from json.decoder import JSONDecodeError
import pandas as pd

from io import BytesIO
import os
import logging
import requests
import json
import sys
from zipfile import ZipFile, BadZipFile

logger = logging.getLogger(__name__)
FORMAT = "[%(asctime)s] %(message)-25s [%(funcName)s():%(filename)8s:%(lineno)s]"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

REQUESTED_FILE = 'annotations/person_keypoints_val2017.json'
coco_url = "http://localhost:8000/test.json"

def download_file(url)->bytes:
    response = requests.get(url)
    if response.status_code != 200:
        logger.critical("Problem with downloading file from: %s", coco_url)
        sys.exit(-1)
    else: logger.info("File downloaded from: %s", coco_url)
    return response.content

def get_zipped_json(file_content) -> tuple:
    try:
        zip_file = ZipFile(BytesIO(file_content))

        """uncomment for, to run script for all files in downloaded zip"""
        # for file_name in list(filter(lambda file_name: file_name == REQUESTED_FILE, zip_file.namelist())):
        for file_name in zip_file.namelist():
            data = json.load(zip_file.open(file_name))
            yield file_name,data

    except BadZipFile:
        logger.info("Provided file is not zipped, trying to extract json directly")
        yield get_unzipped_json(file_content)

def get_unzipped_json(file_content) -> tuple:
    file_name = os.path.basename(coco_url)
    try:
        data = json.loads(file_content.decode('utf-8'))
    except JSONDecodeError:
        logger.critical("Unable to convert downloaded file to JSON, shutdowning... \nAre you sure that url: %s is correct?", coco_url)
        sys.exit(-1)
    return file_name,data


def transform_coco(data) -> pd.DataFrame:
    # select all images out of given dataset
    df_images = pd.DataFrame(data['images'])
    df_images = df_images.set_index('id')
    df_images.index.names = ['image_id'] #for merging readability later

    # pull off image metadata
    df_images_info =  pd.DataFrame(df_images[["file_name","width","height","coco_url"]])
    df_images_info.columns = ["image_name","image_width","image_height","image_url"]

    # all possible image descriptions eg. bounding boxes
    df_annotations = pd.DataFrame(data['annotations'])
    df_annotations = df_annotations.set_index('image_id')

    # extract category_id out of each annotation for labeling later
    df_annotations_category_id = pd.DataFrame(df_annotations["category_id"])

    # done to keep image_id as primary key for relationship between images and annotations
    df_annotations_category_id.reset_index(inplace=True)
    df_annotations_category_id.set_index('category_id', inplace=True)

    # extract all possible categories of objects present at image eg. persons
    df_categories = pd.DataFrame(data['categories'], columns=["id","name"])
    df_categories.set_index('id', inplace=True)

    df_images_category_name = df_annotations_category_id.join(df_categories)
    df_images_category_name.set_index('image_id', inplace=True)
    df_images_category_name.columns = ["label"]

    # pull off image border box coordinates
    df_bbox = pd.DataFrame(df_annotations['bbox'].values.tolist(), columns=["x","y","width","height"], index=df_annotations.index)

    # calculate missing bbox corners
    df_xmax = pd.DataFrame(df_bbox["x"] + df_bbox["width"], columns = ["x_max"], index=df_annotations.index)
    df_ymin = pd.DataFrame(df_bbox["y"] - df_bbox["height"], columns = ["y_min"],index=df_annotations.index)

    # concatenate image corners location
    df_coords = pd.concat([df_bbox["x"], df_ymin, df_xmax, df_bbox["y"]], axis=1)
    df_coords.columns = ["x_min","y_min","x_max","y_max"]

    # merge all dataframes to one
    df_labeled_with_info = pd.merge(df_images_category_name, df_images_info, on=['image_id'])
    df_to_export = pd.merge(df_labeled_with_info, df_coords, on=['image_id'])

    # ensuring that columns order is as requested, you can safely change columns order below 
    # !WARNING! may be computation expensive - could alsoe be done also by single poping/inserting - only image_url is not at position
    final_columns_order = ["label","image_name","image_width","image_height","x_min","y_min","x_max","y_max","image_url"]
    df_to_export = df_to_export.reindex(columns = final_columns_order, copy=False)
    df_to_export.drop_duplicates(inplace=True)
    return df_to_export

def main():
    content = download_file(coco_url)
    coco_data_generator = get_zipped_json(content)
    for file_name, data in coco_data_generator:
        try:
            df = transform_coco(data)
        except KeyError:
            logger.error("Unsupported format in %s, skipping...", file_name)
            continue
        logger.info("Transformed %s ", file_name)
        # print(df)

if __name__ == '__main__':
    main()