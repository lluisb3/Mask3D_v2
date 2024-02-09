import open3d as o3d
from utils.point_cloud_utils import load_ply_pandas
import pandas as pd
import open3d.visualization.gui as gui

def get_floor(filepath, threshold):

    df_ply = load_ply_pandas(filepath)

    floor_z_value = df_ply['Z'].min()

    final_threshold = floor_z_value + abs(threshold*floor_z_value)

    floor_points = df_ply[df_ply['Z'] <= final_threshold]

    floor_df = pd.DataFrame(floor_points)

    pcd = o3d.io.read_triangle_mesh(filepath)
    floor_pcd = pcd.select_by_index(floor_df.index) 
    app = gui.Application.instance
    app.initialize()

    vis = o3d.visualization.O3DVisualizer("Scene Hes·so", 1024, 768)
    vis.show_settings = True

    # Load scene visualization    
    vis.add_geometry(f"Scene", floor_pcd)
    vis.reset_camera_to_default()

    app.add_window(vis)
    app.run()

    return floor_pcd


def main():
    floor_pcd = get_floor("/home/ither1/hl2ss/data/mesh_obj/mesh_obj_mesh.ply", 0.45)


if __name__ == "__main__":
    main()