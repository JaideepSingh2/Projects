# Drowsiness Detector

## Install dependencies

`$ pip install -r requirements.txt`

## Run

For webcam:

`$ python3 ./detector.py`

For video file:

`$ python3 ./detector.py ./hr_test_data/video1.avi`

## Files
### Main Files
[detector.py](./detector.py)- main script for eye detection and heart rate

[eye_detect.py](./eye_detect.py)- measures aspect ratio of eye

[freq_peak.py](./freq_peak.py)- finds the dominant frequency and uses that to calculate BPM

### Heart Rate
[hr_training/read_bdf.py](./hr_training/read_bdf.py)- calculates the heart rate for a given BDF file.
Usage: 

`$ python3 ./hr_training/read_bdf.py ./hr_test_data/data1.bdf`

[hr_training/train_ICA.py](./hr_training/train_ICA.py)- generate ICA unmixing matrix

### Eye Detection
Change lines 27-29 to use different pretrained data.

Pretrained eigeneye and meaneyes:

[eye_training_data/user1_eyes.csv](./eye_training_data/user1_eyes.csv)- light skinned
[eye_training_data/user1and2_eyes.csv](./eye_training_data/user1and2_eyes.csv)- light and dark skinned
[eye_training_data/user3_eyes.csv](./eye_training_data/user3_eyes.csv)- dark skinned

Train your own:

[eye_training/save_training_images.py](./eye_training/save_training_images.py)- saves training images. Requires the directory name to store data (user1_open and user1_close are given as examples), the number of data points to store, and the number to start naming the new images

[eye_training/train_fisher.m](./eye_training/train_fisher.m)- main script. Specify the directory names containing closed eye images and open eye images before running the script. Once the program runs, you will have two things that you will want to save to a single csv file. First, copy and paste the data from the variable called eye into rows 1-30 columns 1-30 (this is the fishereye). Next, copy and paste the data from the variable called meaneye into rows 32-61 columns 1-30. 

## Sample Results
[sample_results](./sample_results)- contains sample images and videos
