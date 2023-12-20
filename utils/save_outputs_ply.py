#visualization.py

import open3d as o3d
import argparse
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_20, CLASS_LABELS_20, SCANNET_COLOR_MAP_20
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_200, CLASS_LABELS_200, SCANNET_COLOR_MAP_200
from utils.ply_double_to_float import ply_double_to_float
from pathlib import Path


def segmentations_to_ply(ply_path, mask_dir, scene_name):
    # Load ply
    scene_mask = o3d.io.read_point_cloud(ply_path)
    all_objects = []
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
        inst.append([inst_i])
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
        points_object = []
        colors_object = []

        for i in range(len(scene_mask.points)):
            if mask[i]:
                # Detect points anc colors of a single object
                points_object.append(scene_mask.points[i])
                colors_object.append(scene_mask.colors[i])

                colors.append([inst_color[0]/255., inst_color[1]/255., inst_color[2]/255.])
                # colors.append(inst_color)

            else:
                colors.append(scene_mask.colors[i])

        object = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points_object))
        object.colors = o3d.utility.Vector3dVector(colors_object)
        all_objects.append((object, label, score))
        scene_mask.colors = o3d.utility.Vector3dVector(colors)


    return scene_mask, all_objects

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

    # Create output folder if does not exist
    Path(output_path).mkdir(parents=True, exist_ok=True)

    # Compute scene PointCloud and PointCloud for all the objects detected
    scene_mask, segmented_objects = segmentations_to_ply(ply_path, mask_dir, scene_name)

    # Save scene PointCloud
    output_file = f"{output_path}/{scene_name}_segmentations.ply"
    o3d.io.write_point_cloud(output_file, scene_mask)
    ply_double_to_float(output_file)
    print(f"Pcd saved in {output_file}")

    # Save PointCloud for every detected object
    for object in segmented_objects:
        segmentation = object[0]
        label = object[1]
        score = object[2]
        output_file = f"{output_path}/{scene_name}_{label}_{score}.ply"
        o3d.io.write_point_cloud(output_file, segmentation)
        ply_double_to_float(output_file)


if __name__ == "__main__":
    main()