import open3d as o3d
from utils.point_cloud_utils import load_ply_pandas
import pandas as pd

def get_floor():

    filepath = "/home/ither1/docker_volume/hl2ss/recordings/scene_meeting_1/scene_meeting_1_pcd.ply"

    df_ply = load_ply_pandas(filepath)

    floor_z_value = df_ply['Z'].min()

    threshold = floor_z_value + abs(0.1*floor_z_value)

    print(threshold)

    floor_points = df_ply[df_ply['Z'] <= threshold]

    floor_df = pd.DataFrame(floor_points)

    print(floor_df)

    pcd = o3d.io.read_point_cloud(filepath)
    floor_pcd = pcd.select_by_index(floor_df.index) 
    o3d.visualization.draw_geometries([floor_pcd])


def main():
    get_floor()


if __name__ == "__main__":
    main()