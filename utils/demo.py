import subprocess
import argparse
import os
import shutil
from pathlib import Path
import open3d as o3d
from datasets.preprocessing.scannet_preprocessing import ScannetPreprocessing
from utils.visualization_gui_pcd import visualize_test
from utils.segmentations_to_ply import segmentations_to_ply
from utils.ply_double_to_float import ply_double_to_float
import numpy as np

thispath = Path(__file__).resolve()

project_dir = str(thispath.parent.parent)

def segment(d_dir, scene):
    # Execute "segmentator" binary for the current ply file
    args = (f"{project_dir}/third_party/ScanNet/Segmentator/segmentator",  # Path to the compiled segmentator binary
            str(f"{d_dir}/{scene}.ply"))
    popen = subprocess.Popen(args)
    popen.wait()

    # Rename the file and move it to the segments_test folder
    os.rename(f"{d_dir}/{scene}.0.010000.segs.json",
              f"{d_dir}/{scene}_vh_clean_2.0.010000.segs.json")
    shutil.move(f"{d_dir}/{scene}_vh_clean_2.0.010000.segs.json",
                f"{project_dir}/data/raw/scannet_test_segments/{scene}_vh_clean_2.0.010000.segs.json")


def preprocess(d_dir):
    # Execute "scannet_preprocessing.py" for the ply file
    prep = ScannetPreprocessing(data_dir=d_dir, save_dir=d_dir, git_repo=d_dir,
                              scannet200=False, modes=("test",))
    
    prep.preprocess()


def instance_segmentation(exp_name, checkpoint):
    # Execute "main_instance_segmentation.py"
    subprocess.run(["python3", f"{project_dir}/main_instance_segmentation.py",  # Path to main_instance_segmentation python file
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
                    "general.topk_per_image=300",
                    "general.use_dbscan=true",
                    "general.dbscan_eps=0.95",
                    "data.voxel_size=0.02"])


def main():
    # Avoid unnecessary warnings Open3D
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)
    
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
    print("===== Running segmentator =====")
    segment(data_dir, scene)

    # Call preprocess function. Runs "scannet_preprocessing.py" only for test split
    print("===== Preprocessing data =====")
    preprocess(data_dir)

    # Call instance_segmentation. Runs "main_instance_segmentation.py" for test split
    print(f"===== Running Mask3D using {checkpoint} checkpoint =====")
    instance_segmentation(exp_name, checkpoint)

    # Visualize results
    # print("========= Visualization ==========")

    # visualize_test(ply_path=f"{data_dir}/scans_test/{scene}/{scene}_vh_clean_2.ply",
    #                mask_dir=f"{thispath.parent.parent}/eval_output/instance_evaluation_{exp_name}_0/decoder_-1",
    #                scene_name=scene)

    # Save results
    output_path = f"{thispath.parent.parent}/eval_output/instance_evaluation_{exp_name}_0/decoder_-1"

    # Compute scene PointCloud and PointCloud for all the objects detected
    scene_mask, segmented_objects, information = segmentations_to_ply(f"{data_dir}/scans_test/{scene}/{scene}_vh_clean_2.ply",
                    f"{thispath.parent.parent}/eval_output/instance_evaluation_{exp_name}_0/decoder_-1", scene)

    # Save center of the objects and axis
    information.to_csv(f"{output_path}/information.csv")
    
    # Save scene PointCloud
    if scene_mask.get_geometry_type() == o3d.geometry.PointCloud.Type.PointCloud:
        output_file = f"{output_path}/scene_segmented_pcd.ply"
        o3d.io.write_point_cloud(output_file, scene_mask)
        ply_double_to_float(output_file)
        print(f"===== PointCloud with segmentations saved =====")
    elif scene_mask.get_geometry_type() == o3d.geometry.TriangleMesh.Type.TriangleMesh:
        output_file = f"{output_path}/scene_segmented_mesh.ply"
        o3d.io.write_triangle_mesh(output_file, scene_mask)
        ply_double_to_float(output_file)
        print(f"===== Mesh with segmentations saved =====")

    # Save PointCloud for every detected object
    if scene_mask.get_geometry_type() == o3d.geometry.PointCloud.Type.PointCloud:
        for object in segmented_objects:
            pcd_segmentation = object[0]
            label = object[1]
            score = object[2]

            output_file = f"{output_path}/{label}_{score}.ply"
            o3d.io.write_point_cloud(output_file, pcd_segmentation)
            ply_double_to_float(output_file)

            pcd_segmentation.estimate_normals()

            # estimate radius for rolling ball
            distances = pcd_segmentation.compute_nearest_neighbor_distance()
            avg_dist = np.mean(distances)
            if avg_dist != 0:
                radius = abs(1.5 * avg_dist)
            else:
                radius = 0.03
            mesh_object = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd_segmentation,
                                                                o3d.utility.DoubleVector([radius, radius * 2]))
            mesh_output_file = f"{output_path}/{label}_{score}.obj"
            o3d.io.write_triangle_mesh(mesh_output_file, mesh_object)
        print(f"===== PointCloud and Mesh for every segmented object saved =====")

    elif scene_mask.get_geometry_type() == o3d.geometry.TriangleMesh.Type.TriangleMesh:
        for object in segmented_objects:
            pcd_segmentation = object[0]
            label = object[1]
            score = object[2]

            output_file = f"{output_path}/{label}_{score}.ply"
            o3d.io.write_point_cloud(output_file, pcd_segmentation)
            ply_double_to_float(output_file)

            pcd_segmentation.estimate_normals()

            # estimate radius for rolling ball
            distances = pcd_segmentation.compute_nearest_neighbor_distance()
            avg_dist = np.mean(distances)
            if avg_dist != 0:
                radius = abs(1.5 * avg_dist)
            else:
                radius = 0.03
            mesh_object = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd_segmentation,
                                                                o3d.utility.DoubleVector([radius, radius * 2]))
            mesh_output_file = f"{output_path}/{label}_{score}.obj"
            o3d.io.write_triangle_mesh(mesh_output_file, mesh_object)
        print(f"===== PointCloud and Mesh for every segmented object saved  =====")


if __name__ == "__main__":
    main()