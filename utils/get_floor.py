import open3d as o3d
from utils.point_cloud_utils import load_ply_pandas
import pandas as pd

def get_floor(filepath, threshold):

    df_ply = load_ply_pandas(filepath)

    floor_z_value = df_ply['Z'].min()

    final_threshold = floor_z_value + abs(threshold*floor_z_value)

    floor_points = df_ply[df_ply['Z'] <= final_threshold]

    floor_df = pd.DataFrame(floor_points)

    pcd = o3d.io.read_point_cloud(filepath)
    floor_pcd = pcd.select_by_index(floor_df.index) 
    # o3d.visualization.draw_geometries([floor_pcd])

    return floor_pcd


def main():
    floor_pcd = get_floor("/home/ither1/docker_volume/hl2ss/recordings/scene_meeting_1/scene_meeting_1_pcd.ply", 0.1)


if __name__ == "__main__":
    main()