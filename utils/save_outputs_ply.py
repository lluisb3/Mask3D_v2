#visualization.py

import open3d as o3d
import numpy as np
import argparse
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_20, CLASS_LABELS_20, SCANNET_COLOR_MAP_20
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_200, CLASS_LABELS_200, SCANNET_COLOR_MAP_200
from utils.ply_double_to_float import ply_double_to_float


def segmentations_to_ply(ply_path, mask_dir, scene_name):
    # Load ply
    scene_mask = o3d.io.read_point_cloud(ply_path)

    # Read txt for the scene
    with open(f"{mask_dir}/{scene_name}.txt") as f:
        lines = f.readlines()

    # Split the lines into file, instance and score and get the label
    inst=[]
    for l in lines:
        file, inst_i, score = l.split()

        if float(score) < 0.8:
            # print("Score too low, skipping iteration\n")
            continue

        # Create array of instances and get label
        inst.append(inst_i)
        try:
            label = CLASS_LABELS_20[VALID_CLASS_IDS_20.index(int(inst_i))]
            print(label)
        except:
            print(f"Skipped {inst_i}")
            continue

        # Read the mask from the file
        with open(f"{mask_dir}/{file}") as f:
            mask = list(map(bool, (map(int, f.readlines()))))

        # Apply the mask with a color
        colors = []
        inst_color = list(SCANNET_COLOR_MAP_20[VALID_CLASS_IDS_20[CLASS_LABELS_20.index(label)]])
        #inst_color = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]

        for i in range(len(scene_mask.points)):
            if mask[i]:
                colors.append([inst_color[0]/255., inst_color[1]/255., inst_color[2]/255.])
                temp = i
                # colors.append(inst_color)

            else:
                colors.append(scene_mask.colors[i])

        scene_mask.colors = o3d.utility.Vector3dVector(colors)

    return scene_mask

def main():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--output_path', type=str, help="Path to saved the .ply file with the colored segmentations", required=True)
    parser.add_argument('--ply_path', type=str, help="Path to .ply original file", required=True)
    parser.add_argument('--mask_dir', type=str, help="Path to eval_output/<exp_name>/decoder -1", required=True)
    parser.add_argument('--scene_name', type=str, help="Name of the scene", required=True)

    # Parse the arguments
    args = parser.parse_args()
    ply_path = args.ply_path
    mask_dir = args.mask_dir
    scene_name = args.scene_name
    output_path = args.output_path

    scene_mask = segmentations_to_ply(ply_path, mask_dir, scene_name)

    output_file = f"{output_path}/{scene_name}_segmentations.ply"
    o3d.io.write_point_cloud(output_file, scene_mask)
    ply_double_to_float(output_file)
    print(f"Pcd saved in {output_file}")


if __name__ == "__main__":
    main()