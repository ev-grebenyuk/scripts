#!/bin/bash
# convert ts video to mp4

for ts in $(ls *.ts) ; do mp4="${ts}.mp4" ; echo "${mp4}" ; ffmpeg -i "${ts}" -c:v h264_videotoolbox -q:v 50 -ac 2 -b:a 1500k -log_level 100 MP4/"${mp4}" ; done
