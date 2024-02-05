import open3d as o3d
from utils.get_floor import get_floor
import argparse


def get_object(filepath_object, filepath_scene, threshold):

    pcd_object = o3d.io.read_point_cloud(filepath_object)
    pcd_floor = get_floor(filepath_scene, threshold)

    pcd_merge = pcd_floor + pcd_object
    o3d.visualization.draw_geometries([pcd_merge])


def main():
     # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--filepath_object', type=str, required=True)
    # parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--filepath_scene', type=str, required=True)
    parser.add_argument('--threshold', type=float, required=True)

    # Parse the arguments
    args = parser.parse_args()
    filepath_object = args.filepath_object
    filepath_scene = args.filepath_scene
    threshold = args.threshold

    # filepath_object = "D:\Users\appit\docker_volume\mask3d\scene_meeting_3\scene0001_00_chair_0.9861959218978882.ply"
    # filepath_scene = "D:\Users\appit\docker_volume\hl2ss\recordings\scene_meeting_3\scene_meeting_3_pcd.ply"
    get_object(filepath_object, filepath_scene, threshold)


if __name__ == "__main__":
    main()
