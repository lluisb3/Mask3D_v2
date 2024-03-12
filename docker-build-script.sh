#!/bin/sh
# bash script to create image mapping host user's ID with non-root user in the container #

IMAGE=lluisb3/mask3d:v16.0

docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -t $IMAGE .
