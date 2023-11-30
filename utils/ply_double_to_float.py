import os
import numpy as np
from plyfile import PlyData, PlyProperty
import click


def load_ply(filepath):
    plydata = PlyData.read(filepath)
    data = plydata.elements[0].data
    coords = np.array([data['x'], data['y'], data['z']], dtype=np.float32).T
    feats = np.array([data['red'], data['green'], data['blue']], dtype=np.float32).T

    return coords, feats


def check_properties(mesh):
    mesh.compute_vertex_normals()

    edge_manifold = mesh.is_edge_manifold(allow_boundary_edges=True)
    edge_manifold_boundary = mesh.is_edge_manifold(allow_boundary_edges=False)
    vertex_manifold = mesh.is_vertex_manifold()
    self_intersecting = mesh.is_self_intersecting()
    watertight = mesh.is_watertight()
    orientable = mesh.is_orientable()

    print(f"  edge_manifold:          {edge_manifold}")
    print(f"  edge_manifold_boundary: {edge_manifold_boundary}")
    print(f"  vertex_manifold:        {vertex_manifold}")
    print(f"  self_intersecting:      {self_intersecting}")
    print(f"  watertight:             {watertight}")
    print(f"  orientable:             {orientable}")

def ply_double_to_float(ply_path):
    plydata = PlyData.read(ply_path)

    #go through all property one by one and if it is a double, we change it to an equivalent property in float
    real_properties = []
    for i in plydata.elements[0].properties:
        if str(PlyProperty(i.name, "double")) == str(i):
            real_properties.append(PlyProperty(i.name, "float32"))
        else:
            real_properties.append(i)
    real_properties = tuple(real_properties)

    #Save the same ply file but with float properties instead of double
    plydata.elements[0].properties = real_properties

    #Write the data back to the original pointcloudt
    os.remove(ply_path)
    plydata.write(ply_path)


@click.command()
@click.option(
    "--ply_path",
    default="scene",
    prompt="Path to .ply file to convert double to float",
    help="Path to .ply file to convert double to float",
)
def main(ply_path):
    ply_double_to_float(ply_path)


if __name__=="__main__":
    main()
