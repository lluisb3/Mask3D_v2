#segmentations_to_ply.py

import open3d as o3d
import argparse
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_20, CLASS_LABELS_20, SCANNET_COLOR_MAP_20
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_200, CLASS_LABELS_200, SCANNET_COLOR_MAP_200
from utils.ply_double_to_float import ply_double_to_float
from pathlib import Path
from plyfile import PlyData
import pandas as pd
import numpy as np


def segmentations_to_ply(ply_path, mask_dir, scene_name):
    # Check if .ply is a PointCloud or a Mesh
    with open(ply_path, "rb") as f:
        plydata = PlyData.read(f)
    number_of_elements_ply = len(plydata.elements)  # 1 for pcd, 2 for mesh
    f.close()

    # Load ply
    if number_of_elements_ply <= 1:
        scene_mask = o3d.io.read_point_cloud(ply_path)
    else:
        scene_mask = o3d.io.read_triangle_mesh(ply_path)
    
    # Rotation matrices to coordinate system in Unity
    rotation_unity = np.array(([1.0, 0.0, 0.0],
                    [0.0, 0.0, -1.0],
                    [0.0, -1.0, 0.0]))
    
    rotation_unity_2 = np.array(([-1.0, -0.0, 0.0],
                    [0.0, -1.0, 0.0],
                    [0.0, 0.0, 1.0]))

    all_objects = []
    information = []
    header = ["object", "score", "center", "axis_aligned_bounding_box", "axis_points", "axis_center", "oriented_bounding_box", "oriented_points", "oriented_center"]
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

        # Check if input is a PointCloud (number_of_elements_ply <= 1) else a Mesh 
        if number_of_elements_ply <= 1:
            for i in range(len(scene_mask.points)):
                if mask[i]:
                    # Detect points anc colors of a single object
                    points_object.append(scene_mask.points[i])
                    colors_object.append(scene_mask.colors[i])

                    colors.append([inst_color[0]/255., inst_color[1]/255., inst_color[2]/255.])
                    # colors.append(inst_color)

                else:
                    colors.append(scene_mask.colors[i])

            object_pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points_object))
            object_pcd.colors = o3d.utility.Vector3dVector(colors_object)

            # Rotate objects to unity coordinate system
            object_pcd.rotate(rotation_unity, center=(0, 0, 0))
            object_pcd.rotate(rotation_unity_2, center=(0, 0, 0))

            # Remove outlier points in the PointCloud
            print("Statistical outlier removal")
            _, ind = object_pcd.remove_statistical_outlier(nb_neighbors=25,
                                                    std_ratio=0.8)
            object_pcd_inliers = object_pcd.select_by_index(ind)

            # If object has enough points
            if len(object_pcd_inliers.points) > 3:
                center_object = object_pcd_inliers.get_center()
                axis_aligned_bounding_box = object_pcd_inliers.get_axis_aligned_bounding_box()
                axis_aligned_points = np.asarray(axis_aligned_bounding_box.get_box_points())
                axis_aligned_center = axis_aligned_bounding_box.get_center()
                oriented_bounding_box = object_pcd_inliers.get_oriented_bounding_box()
                oriented_points = np.asarray(oriented_bounding_box.get_box_points())
                oriented_center = oriented_bounding_box.get_center()
            else:
                center_object = None
                axis_aligned_bounding_box = None
                axis_aligned_points = None
                axis_aligned_center = None
                oriented_bounding_box = None
                oriented_points = None
                oriented_center = None
            
            all_objects.append((object_pcd_inliers, label, score))
            information.append((label, score, center_object, axis_aligned_bounding_box, axis_aligned_points, axis_aligned_center, oriented_bounding_box, oriented_points, oriented_center))
            pcd_dataframe_information = pd.DataFrame(information, columns=header)
            scene_mask.colors = o3d.utility.Vector3dVector(colors)
        # Mesh
        else:
            for i in range(len(scene_mask.vertices)):
                if mask[i]:
                    # Detect points anc colors of a single object
                    points_object.append(scene_mask.vertices[i])
                    colors_object.append(scene_mask.vertex_colors[i])

                    colors.append([inst_color[0]/255., inst_color[1]/255., inst_color[2]/255.])
                    # colors.append(inst_color)

                else:
                    colors.append(scene_mask.vertex_colors[i])

            object_pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points_object))
            object_pcd.colors = o3d.utility.Vector3dVector(colors_object)

            # Rotate objects to unity coordinate system
            object_pcd.rotate(rotation_unity, center=(0, 0, 0))
            object_pcd.rotate(rotation_unity_2, center=(0, 0, 0))

            # Remove outlier points in the PointCloud
            print("Statistical outlier removal")
            _, ind = object_pcd.remove_statistical_outlier(nb_neighbors=25,
                                                    std_ratio=0.8)
            object_pcd_inliers = object_pcd.select_by_index(ind)

            center_object = object_pcd_inliers.get_center()
            if len(object_pcd_inliers.points) > 3:
                center_object = object_pcd_inliers.get_center()
                axis_aligned_bounding_box = object_pcd_inliers.get_axis_aligned_bounding_box()
                axis_aligned_points = np.asarray(axis_aligned_bounding_box.get_box_points())
                axis_aligned_center = axis_aligned_bounding_box.get_center()
                oriented_bounding_box = object_pcd_inliers.get_oriented_bounding_box()
                oriented_points = np.asarray(oriented_bounding_box.get_box_points())
                oriented_center = oriented_bounding_box.get_center()
            else:
                center_object = None
                axis_aligned_bounding_box = None
                axis_aligned_points = None
                axis_aligned_center = None
                oriented_bounding_box = None
                oriented_points = None
                oriented_center = None

            
            all_objects.append((object_pcd_inliers, label, score))
            information.append((label, score, center_object, axis_aligned_bounding_box, axis_aligned_points, axis_aligned_center, oriented_bounding_box, oriented_points, oriented_center))

            pcd_dataframe_information = pd.DataFrame(information, columns=header)
            scene_mask.vertex_colors = o3d.utility.Vector3dVector(colors)

    return scene_mask, all_objects, pcd_dataframe_information

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
        output_file = f"{output_path}/{label}_{score}.ply"
        o3d.io.write_point_cloud(output_file, segmentation)
        ply_double_to_float(output_file)


if __name__ == "__main__":
    main()