#!/bin/bash
export OMP_NUM_THREADS=3  # speeds up MinkowskiEngine

CURR_DBSCAN=0.95
CURR_TOPK=500
CURR_QUERY=150

# TEST
python main_instance_segmentation.py \
general.experiment_name="test_v8" \
general.project_name="scannet_eval" \
general.checkpoint='checkpoints/scannet/scannet_val.ckpt' \
general.train_mode=false \
general.eval_on_segments=true \
general.train_on_segments=true \
general.save_visualizations=true \
general.export=true \
model.num_queries=${CURR_QUERY} \
general.topk_per_image=${CURR_TOPK} \
general.use_dbscan=true \
general.dbscan_eps=${CURR_DBSCAN} \
data.test_mode=test \
data.voxel_size=0.05