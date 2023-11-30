#visualization.py

import open3d as o3d
import open3d.visualization.gui as gui
import argparse
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_20, CLASS_LABELS_20, SCANNET_COLOR_MAP_20
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_200, CLASS_LABELS_200, SCANNET_COLOR_MAP_200


def visualize_test(ply_path, mask_dir, scene_name):
    # Load ply
    scene_mask = o3d.io.read_point_cloud(ply_path)

    # Initialize visualizer
    app = gui.Application.instance
    app.initialize()

    vis = o3d.visualization.O3DVisualizer("Scene Hes·so", 1024, 768)
    vis.show_settings = True

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

        # if mask.count(1) < 100:
        #     continue

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
        vis.add_3d_label(scene_mask.points[temp], "{}".format(label))

    # Load scene visualization    
    vis.add_geometry(f"Scene {scene_name}", scene_mask)
    vis.reset_camera_to_default()

    app.add_window(vis)
    app.run()


def main():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--ply_path', type=str, help="Path to .ply original file", required=True)
    parser.add_argument('--mask_dir', type=str, help="Path to eval_output/<exp_name>/decoder -1", required=True)
    parser.add_argument('--scene_name', type=str, help="Name of the scene", required=True)

    # Parse the arguments
    args = parser.parse_args()
    ply_path = args.ply_path
    mask_dir = args.mask_dir
    scene_name = args.scene_name

    visualize_test(ply_path, mask_dir, scene_name)


if __name__ == "__main__":
    main()
