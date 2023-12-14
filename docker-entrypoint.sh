#!/bin/sh

CHECKPOINT=scannet_best
SCENE=scene0001_00

python3 -m utils.demo --scene $SCENE --exp_name docker --checkpoint $CHECKPOINT
