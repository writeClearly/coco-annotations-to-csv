## Overview
This script downloads annotations in [COCO format](https://cocodataset.org/#format-data), extracts its metadata and saves result to the specifed directory in .csv

[<img src="https://cocodataset.org/images/detection-splash.png">](https://cocodataset.org/#detection-2019)

## Features
- converts each annotation to single csv row
- calculates edge locations for annotations
- supports input in .zip or .json
- all extracting/unzipping is done in memory without saving to the disk
- custom logging
- progress bar
- easily dockerized via Dockerfile



## Result Format
<img src="https://i.postimg.cc/MGxBcLjR/result-CSV.png">

## Usage
### Local
```bash
git clone 
cd coco-annotations-to-csv
pip install -r requirements.txt
echo "export PATH=$PATH:/PATH/WHERE/YOU/CLONED/coco-annotations-to-csv/" >> $HOME/.bashrc 
# bash reload needed
coco2csv -s https://images.cocodataset.org/annotations/annotations_trainval2017.zip -d ~/Downloads
```
### Docker
```bash
git clone 
cd coco-annotations-to-csv
docker build -t coco2csv:1.0 .
docker run --rm -it --entrypoint /bin/bash coco2csv:1.0
coco2csv -s https://images.cocodataset.org/annotations/annotations_trainval2017.zip -d ~/Downloads
```