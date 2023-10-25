#visualization.py

import open3d as o3d
import open3d.visualization.gui as gui
import numpy as np
import argparse
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_20, CLASS_LABELS_20, SCANNET_COLOR_MAP_20
from datasets.scannet200.scannet200_constants import VALID_CLASS_IDS_200, CLASS_LABELS_200, SCANNET_COLOR_MAP_200
import random
from PIL import Image, ImageFont, ImageDraw
from pyquaternion import Quaternion

def text_3d(text, pos, direction=None, degree=0.0, font="/usr/share/fonts/truetype/lato/Lato-Medium.ttf", font_size=500, density=1):
    """
    Generate a 3D text point cloud used for visualization.
    :param text: content of the text
    :param pos: 3D xyz position of the text upper left corner
    :param direction: 3D normalized direction of where the text faces
    :param degree: in plane rotation of text
    :param font: Name of the font - change it according to your system
    :param font_size: size of the font
    :return: o3d.geoemtry.PointCloud object
    """
    if direction is None:
        direction = (0., 0., 1.)

    font_obj = ImageFont.truetype(font, font_size * density)
    font_dim = font_obj.getsize(text)

    img = Image.new('RGB', font_dim, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font_obj, fill=(0, 0, 0))
    img = np.asarray(img)
    img_mask = img[:, :, 0] < 128
    indices = np.indices([*img.shape[0:2], 1])[:, img_mask, 0].reshape(3, -1).T

    pcd = o3d.geometry.PointCloud()
    pcd.colors = o3d.utility.Vector3dVector(img[img_mask, :].astype(float) / 255.0)
    pcd.points = o3d.utility.Vector3dVector(indices / 1000 / density)

    raxis = np.cross([0.0, 0.0, 1.0], direction)
    if np.linalg.norm(raxis) < 1e-6:
        raxis = (0.0, 0.0, 1.0)
    trans = (Quaternion(axis=raxis, radians=np.arccos(direction[2])) *
             Quaternion(axis=direction, degrees=degree)).transformation_matrix
    trans[0:3, 3] = np.asarray(pos)
    pcd.transform(trans)
    return pcd


def main():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--ply_path', type=str, required=True)
    parser.add_argument('--mask_dir', type=str, required=True)
    parser.add_argument('--scene_name', type=str, required=True)
    parser.add_argument('--ext', action="store_true")

    # Parse the arguments
    args = parser.parse_args()
    ply_path = args.ply_path
    mask_dir = args.mask_dir
    scene_name = args.scene_name

    # Load ply
    scene_mask = o3d.io.read_point_cloud(ply_path)

    # Read txt for the scene
    with open(mask_dir + "/" + scene_name + ".txt") as f:
        lines = f.readlines()

    # Split the lines into file, instance and score and get the label
    inst=[]
    text_labels = []
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
            print("Skipped " + inst_i)
            continue

        # Read the mask from the file
        with open(mask_dir + "/" + file) as f:
            mask = list(map(bool, (map(int, f.readlines()))))

        # Apply the mask with a color
        colors = []
        inst_color = list(SCANNET_COLOR_MAP_20[VALID_CLASS_IDS_20[CLASS_LABELS_20.index(label)]])
        #inst_color = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
        temp = []
        for i in range(len(scene_mask.points)):
            if mask[i]:
                colors.append([inst_color[0]/255., inst_color[1]/255., inst_color[2]/255.])
                temp.append(i)
                # colors.append(inst_color)

            else:
                colors.append(scene_mask.colors[i])
        center_instance = int(len(temp)/2)
        scene_mask.colors = o3d.utility.Vector3dVector(colors)
        text = text_3d(text=label, pos=np.asarray(scene_mask.points[temp[center_instance]]), degree=270.0)
        text_labels.append(text)

    # Visualize scene
    if args.ext:
        ev = o3d.visualization.ExternalVisualizer()
        ev.set(scene_mask,text)
    else:
        ev = o3d.visualization.Visualizer()
        ev.create_window()
        ev.add_geometry(scene_mask)
        for text in text_labels:
            ev.add_geometry(text)
        ev.run()
        ev.destroy_window()


if __name__ == "__main__":
    main()