import subprocess
import argparse
import os
import shutil
from pathlib import Path
from datasets.preprocessing.scannet_preprocessing import ScannetPreprocessing
from utils.visualization_gui import visualize_test
import json
import plyfile
import numpy as np

thispath = Path(__file__).resolve()

project_dir = str(thispath.parent.parent)

def segment(d_dir, scene):
    # # Execute "segmentator" binary for the current ply file
    # args = (f"{project_dir}/third_party/ScanNet/Segmentator/segmentator",  # Path to the compiled segmentator binary
    #         str(f"{d_dir}/{scene}.ply"))
    # popen = subprocess.Popen(args)
    # popen.wait()

    plydata = plyfile.PlyData.read(f"{d_dir}/{scene}.ply")

    data = plydata.elements[0].data
    coords = np.array([data['x'], data['y'], data['z']], dtype=np.float32).T

    # Opening JSON file
    f = open('data/raw/scannet_test_segments/scene3333_00_vh_clean_2.0.010000.segs.json')

    a = open(f'data/raw/scannet_test_segments/{scene}_vh_clean_2.0.010000.segs.json', 'w')
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    data_a = data
    
    # Iterating through the json
    # list
    data_a['segIndices'] = list(range(len(coords)))

    json.dump(data_a, a, indent = 6)  
    
    # Closing file
    f.close()
    a.close()

    # Rename the file and move it to the segments_test folder
    # os.rename(f"{d_dir}/{scene}.0.010000.segs.json",
    #           f"{d_dir}/{scene}_vh_clean_2.0.010000.segs.json")
    # shutil.move(f"{d_dir}/{scene}_vh_clean_2.0.010000.segs.json",
    #             f"{project_dir}/data/raw/scannet_test_segments/{scene}_vh_clean_2.0.010000.segs.json")


def preprocess(d_dir):
    # Execute "scannet_preprocessing.py" for the ply file
    prep = ScannetPreprocessing(data_dir=d_dir, save_dir=d_dir, git_repo=d_dir,
                              scannet200=False, modes=("test",))
    
    prep.preprocess()


def instance_segmentation(exp_name, checkpoint):
    # Execute "main_instance_segmentation.py"
    subprocess.run(["python", f"{project_dir}/main_instance_segmentation.py",  # Path to main_instance_segmentation python file
                    f"general.experiment_name={exp_name}",
                    "general.project_name='scannet_eval'",
                    f"general.checkpoint='checkpoints/scannet/{checkpoint}.ckpt'",  # Path to checkpoint
                    "general.eval_on_segments=true",
                    "general.train_on_segments=true",
                    "general.train_mode=false",
                    "general.export=true",
                    "data.test_mode=test",  # Use test split
                    "data/datasets=demo",  # Copy of scannet.yaml with test_dataset.data_dir changed
                    "model.num_queries=150",
                    "general.topk_per_image=500",
                    "general.use_dbscan=true",
                    "general.dbscan_eps=0.95",
                    "data.voxel_size=0.05"])

def main():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--exp_name', type=str, required=True)
    # parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--scene', type=str, required=True)
    parser.add_argument('--checkpoint', type=str, required=True)

    # Parse the arguments
    args = parser.parse_args()
    exp_name = args.exp_name
    # data_dir = args.data_dir
    scene = args.scene
    checkpoint = args.checkpoint

    data_dir = str(f"{project_dir}/data/raw/hesso")


    # Update txt of the test split with the scene name
    f = open(f"{data_dir}/Tasks/Benchmark/scannetv2_test.txt", "w")
    f.write(f"{scene}\n")
    f.close()

    # Check if the folders exist, create them if not
    if not os.path.exists(f"{data_dir}/scans_test"):
        os.mkdir(f"{data_dir}/scans_test")
    if not os.path.exists(f"{data_dir}/scans_test/{scene}"):
        os.mkdir(f"{data_dir}/scans_test/{scene}")

    # Rename file and move it to ./scans_test/<scene>/
    shutil.copy(f"{data_dir}/{scene}.ply", f"{data_dir}/scans_test/{scene}/{scene}_vh_clean_2.ply")

    # Call segment function. Runs segmentator on the file and moves the output to the segments_test folder
    print("========= Running segmentator ==========")
    segment(data_dir, scene)

    # Call preprocess function. Runs "scannet_preprocessing.py" only for test split
    print("========= Preprocessing data ==========")
    preprocess(data_dir)

    # Call instance_segmentation. Runs "main_instance_segmentation.py" for test split
    print(f"========= Running Mask3D using {checkpoint} checkpoint ==========")
    instance_segmentation(exp_name, checkpoint)

    # Visualize results
    print("========= Visualization ==========")
    visualize_test(ply_path=f"{data_dir}/scans_test/{scene}/{scene}_vh_clean_2.ply",
                   mask_dir=f"{thispath.parent.parent}/eval_output/instance_evaluation_{exp_name}_0/decoder_-1",
                   scene_name=scene)


if __name__ == "__main__":
    main()